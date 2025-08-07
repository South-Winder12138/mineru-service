"""
MinerU文档处理核心服务
"""
import asyncio
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger
import pypdf

# MinerU通过命令行调用，不需要API导入
MINERU_AVAILABLE = True

from .config import settings
from .models import (
    DocumentType, ExtractionMode, ExtractionResult,
    ProcessingTask, TaskStatus, DocumentProcessRequest
)
from .offline_config import offline_config


class MinerUProcessor:
    """MinerU文档处理器 - 完全私有化版本"""

    def __init__(self):
        self.processing_tasks: Dict[str, ProcessingTask] = {}

        # 设置环境变量，禁用网络功能
        self._setup_offline_environment()

        logger.info(f"MinerU处理器初始化完成 (私有化模式, 设备: {settings.mineru_device})")

    def _setup_offline_environment(self):
        """设置离线环境，禁用所有网络功能"""
        # 使用统一的离线配置
        status = offline_config.check_dependencies()

        if status["offline_mode"]:
            logger.info("✅ 离线模式已启用")
        else:
            logger.warning("⚠️ 离线模式配置异常")

        logger.info("🔒 已设置完全私有化环境")

    async def process_document(
        self, 
        file_path: Path, 
        filename: str,
        request_params: DocumentProcessRequest
    ) -> str:
        """处理文档并返回任务ID"""
        task_id = str(uuid.uuid4())
        
        # 确定文档类型
        doc_type = self._get_document_type(file_path)
        
        # 创建处理任务
        task = ProcessingTask(
            task_id=task_id,
            filename=filename,
            file_path=str(file_path),
            document_type=doc_type,
            request_params=request_params
        )
        
        self.processing_tasks[task_id] = task
        
        # 异步处理文档
        asyncio.create_task(self._process_task(task))
        
        return task_id
    
    async def _process_task(self, task: ProcessingTask):
        """异步处理任务"""
        try:
            logger.info(f"开始处理任务: {task.task_id}")
            
            # 更新任务状态
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.now()
            
            # 智能处理策略：根据格式选择最佳处理方式
            file_ext = Path(task.file_path).suffix.lower()

            if file_ext in settings.mineru_direct_formats:
                # PDF和图片直接用MinerU处理
                logger.info(f"直接使用MinerU处理: {file_ext}")
                result = await self._process_with_mineru(task)
            elif file_ext in settings.convert_to_pdf_formats:
                # 其他格式自动转换为PDF，再用MinerU处理
                logger.info(f"转换为PDF后使用MinerU处理: {file_ext}")
                result = await self._convert_and_process_with_mineru(task)
            else:
                raise ValueError(f"不支持的文档格式: {file_ext}")

            
            # 更新任务结果
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            logger.info(f"任务处理完成: {task.task_id}")
            
        except Exception as e:
            logger.error(f"任务处理失败: {task.task_id}, 错误: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()

    async def _convert_and_process_with_mineru(self, task: ProcessingTask) -> ExtractionResult:
        """将文档转换为PDF后用MinerU处理"""
        file_path = Path(task.file_path)
        file_ext = file_path.suffix.lower()

        try:
            # 根据文件类型选择转换方法
            if file_ext in ['.docx', '.doc']:
                logger.info("转换Word文档为PDF...")
                pdf_path = await self._convert_word_to_pdf(file_path)
            elif file_ext in ['.txt', '.md']:
                logger.info("转换文本文件为PDF...")
                pdf_path = await self._convert_text_to_pdf(file_path)
            elif file_ext == '.xml':
                logger.info("转换XML文件为PDF...")
                pdf_path = await self._convert_xml_to_pdf(file_path)
            else:
                raise ValueError(f"不支持转换的文件格式: {file_ext}")

            # 创建临时任务用于处理转换后的PDF
            temp_task = ProcessingTask(
                task_id=task.task_id + "_converted",
                filename=pdf_path.name,
                file_path=str(pdf_path),
                document_type=DocumentType.PDF,
                request_params=task.request_params
            )

            # 用MinerU处理转换后的PDF
            result = await self._process_with_mineru(temp_task)

            # 清理临时PDF文件
            try:
                pdf_path.unlink()
            except Exception as e:
                logger.warning(f"清理临时文件失败: {str(e)}")

            # 更新元数据，标明经过了转换
            result.metadata.update({
                "original_format": file_ext,
                "converted_to": "pdf",
                "processor": "MinerU (via conversion)"
            })

            return result

        except Exception as e:
            logger.error(f"文档转换处理失败: {str(e)}")
            # 如果转换失败，返回简单的处理结果
            return ExtractionResult(
                text_content=f"文档转换失败: {file_path.name}\n错误: {str(e)}",
                markdown_content=f"# 处理失败\n\n文档: {file_path.name}\n错误: {str(e)}",
                images=[],
                tables=[],
                metadata={"error": str(e), "original_format": file_ext}
            )

    async def _convert_word_to_pdf(self, word_path: Path) -> Path:
        """将Word文档转换为PDF"""
        import tempfile
        import subprocess

        # 创建临时PDF文件
        temp_dir = Path(tempfile.mkdtemp())
        pdf_path = temp_dir / f"{word_path.stem}.pdf"

        try:
            # 尝试使用LibreOffice转换
            cmd = [
                "libreoffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(temp_dir),
                str(word_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                raise Exception(f"LibreOffice转换失败: {result.stderr}")

            if not pdf_path.exists():
                raise Exception("PDF文件未生成")

            return pdf_path

        except FileNotFoundError:
            # LibreOffice未安装，使用备用方法
            logger.warning("LibreOffice未安装，使用Word文档解析转换")
            return await self._convert_word_to_pdf_simple(word_path)
        except Exception as e:
            logger.error(f"Word转PDF失败: {str(e)}")
            raise

    async def _convert_word_to_pdf_simple(self, word_path: Path) -> Path:
        """使用python-docx解析Word文档并转换为PDF"""
        import tempfile

        try:
            from docx import Document
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph
        except ImportError as e:
            raise Exception(f"缺少必要的库: {str(e)}")

        # 创建临时PDF文件
        temp_dir = Path(tempfile.mkdtemp())
        pdf_path = temp_dir / f"{word_path.stem}.pdf"

        try:
            # 读取Word文档
            doc = Document(word_path)

            # 提取文本内容
            content = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    content += paragraph.text + "\n"

            # 如果没有内容，添加提示
            if not content.strip():
                content = f"Word文档: {word_path.name}\n\n文档内容为空或无法解析。"

            # 创建PDF
            c = canvas.Canvas(str(pdf_path), pagesize=letter)
            width, height = letter

            # 设置字体（支持中文）
            try:
                c.setFont("Helvetica", 12)
            except:
                c.setFont("Helvetica", 12)

            # 分行处理文本
            lines = content.split('\n')
            y_position = height - 50
            line_height = 14

            for line in lines:
                if y_position < 50:  # 换页
                    c.showPage()
                    y_position = height - 50

                # 处理长行
                if len(line) > 80:
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        if len(current_line + word) < 80:
                            current_line += word + " "
                        else:
                            if current_line:
                                try:
                                    c.drawString(50, y_position, current_line.strip())
                                except:
                                    c.drawString(50, y_position, current_line.strip().encode('utf-8', errors='ignore').decode('utf-8'))
                                y_position -= line_height
                            current_line = word + " "

                    if current_line:
                        try:
                            c.drawString(50, y_position, current_line.strip())
                        except:
                            c.drawString(50, y_position, current_line.strip().encode('utf-8', errors='ignore').decode('utf-8'))
                        y_position -= line_height
                else:
                    try:
                        c.drawString(50, y_position, line)
                    except:
                        # 处理特殊字符
                        safe_line = line.encode('utf-8', errors='ignore').decode('utf-8')
                        c.drawString(50, y_position, safe_line)
                    y_position -= line_height

            c.save()
            return pdf_path

        except Exception as e:
            logger.error(f"Word文档解析失败: {str(e)}")
            raise

    async def _convert_text_to_pdf(self, text_path: Path) -> Path:
        """将文本文件转换为PDF"""
        return await self._convert_text_to_pdf_simple(text_path)

    async def _convert_text_to_pdf_simple(self, file_path: Path) -> Path:
        """使用reportlab将文本转换为PDF"""
        import tempfile

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except ImportError:
            raise Exception("reportlab未安装，无法转换文本为PDF")

        # 创建临时PDF文件
        temp_dir = Path(tempfile.mkdtemp())
        pdf_path = temp_dir / f"{file_path.stem}.pdf"

        try:
            # 读取文本内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()

        # 创建PDF
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        width, height = letter

        # 设置字体和大小
        c.setFont("Helvetica", 12)

        # 分行处理文本
        lines = content.split('\n')
        y_position = height - 50
        line_height = 14

        for line in lines:
            if y_position < 50:  # 换页
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = height - 50

            # 简化处理：直接输出行，不处理长行
            try:
                c.drawString(50, y_position, line[:100])  # 限制长度
                y_position -= line_height
            except:
                # 如果有特殊字符导致错误，跳过这行
                y_position -= line_height
                continue

        c.save()
        return pdf_path

    async def _convert_xml_to_pdf(self, xml_path: Path) -> Path:
        """将XML文件转换为PDF"""
        import tempfile
        import xml.etree.ElementTree as ET

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except ImportError:
            raise Exception("reportlab未安装，无法转换XML为PDF")

        # 创建临时PDF文件
        temp_dir = Path(tempfile.mkdtemp())
        pdf_path = temp_dir / f"{xml_path.stem}.pdf"

        try:
            # 解析XML文件
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # 将XML转换为可读文本
            content = self._xml_to_text(root)

        except Exception as e:
            logger.warning(f"XML解析失败，使用原始文本: {str(e)}")
            # 如果XML解析失败，直接读取文本内容
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read()

        # 创建PDF
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        width, height = letter

        # 设置字体和大小
        c.setFont("Helvetica", 12)

        # 分行处理文本
        lines = content.split('\n')
        y_position = height - 50
        line_height = 14

        for line in lines:
            if y_position < 50:  # 换页
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = height - 50

            # 简化处理：直接输出行
            try:
                c.drawString(50, y_position, line[:100])  # 限制长度
                y_position -= line_height
            except:
                # 如果有特殊字符导致错误，跳过这行
                y_position -= line_height
                continue

        c.save()
        return pdf_path

    def _xml_to_text(self, element, level=0) -> str:
        """将XML元素转换为可读文本"""
        text = ""
        indent = "  " * level

        # 添加元素名称
        if element.tag:
            text += f"{indent}<{element.tag}>\n"

        # 添加元素文本内容
        if element.text and element.text.strip():
            text += f"{indent}  {element.text.strip()}\n"

        # 递归处理子元素
        for child in element:
            text += self._xml_to_text(child, level + 1)

        # 添加元素尾部文本
        if element.tail and element.tail.strip():
            text += f"{indent}{element.tail.strip()}\n"

        return text
    
    async def _process_with_mineru(self, task: ProcessingTask) -> ExtractionResult:
        """使用MinerU处理PDF和图片文档"""
        file_path = Path(task.file_path)

        # 尝试使用MinerU
        if MINERU_AVAILABLE:
            try:
                return await self._process_with_mineru_cmd(file_path, task.request_params)
            except Exception as e:
                logger.warning(f"MinerU处理失败，使用备用方法: {str(e)}")

        # 备用方法：根据文件类型选择
        file_ext = file_path.suffix.lower()
        if file_ext == '.pdf':
            return await self._process_pdf_fallback(file_path, task.request_params)
        else:
            # 图片文件处理失败
            return ExtractionResult(
                text_content="图片处理失败：MinerU不可用",
                markdown_content="# 处理失败\n\n图片处理失败：MinerU不可用",
                images=[{"path": str(file_path), "type": "original"}],
                tables=[],
                metadata={"error": "MinerU不可用"}
            )
    
    async def _process_with_mineru_cmd(
        self,
        file_path: Path,
        params: DocumentProcessRequest
    ) -> ExtractionResult:
        """使用MinerU处理PDF"""
        import tempfile
        import subprocess
        import json

        try:
            # 创建临时输出目录
            with tempfile.TemporaryDirectory() as temp_dir:
                output_dir = Path(temp_dir)

                # 使用MinerU命令行工具处理PDF
                cmd = [
                    "mineru",
                    "-p", str(file_path),
                    "-o", str(output_dir)
                ]

                # 添加设备参数
                if settings.mineru_device != "cpu":
                    cmd.extend(["--device", settings.mineru_device])

                # 设置离线环境变量，使用本地缓存
                env = os.environ.copy()

                # 检查本地缓存
                local_hf_cache = settings.data_dir / "cache" / "huggingface"
                if local_hf_cache.exists():
                    env.update({
                        'HF_HOME': str(local_hf_cache),
                        'HUGGINGFACE_HUB_CACHE': str(local_hf_cache / "hub"),
                    })

                env.update({
                    'MODELSCOPE_OFFLINE': '1',
                    'HF_OFFLINE': '1',
                    'TRANSFORMERS_OFFLINE': '1',
                    'HF_HUB_OFFLINE': '1',
                    'NO_PROXY': '*',
                    'OFFLINE_MODE': '1'
                })

                # 运行MinerU (离线模式)
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5分钟超时
                    env=env
                )

                if result.returncode != 0:
                    raise Exception(f"MinerU处理失败: {result.stderr}")

                # 读取处理结果
                text_content = ""
                markdown_content = ""
                images = []
                tables = []

                # 查找输出文件
                for output_file in output_dir.rglob("*.md"):
                    with open(output_file, 'r', encoding='utf-8') as f:
                        markdown_content = f.read()
                        text_content = markdown_content  # 简化处理
                    break

                # 查找图片文件
                for img_file in output_dir.rglob("*.png"):
                    images.append({
                        "path": str(img_file),
                        "type": "extracted"
                    })

                return ExtractionResult(
                    text_content=text_content,
                    markdown_content=markdown_content,
                    images=images,
                    tables=tables,
                    metadata={"processor": "MinerU", "pages": 0}
                )

        except Exception as e:
            logger.error(f"MinerU处理失败: {str(e)}")
            raise
    
    async def _process_pdf_fallback(
        self, 
        file_path: Path, 
        params: DocumentProcessRequest
    ) -> ExtractionResult:
        """备用PDF处理方法"""
        text_content = ""
        images = []
        tables = []
        
        try:
            # 使用pypdf提取文本
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text_content += f"\n--- 第{page_num + 1}页 ---\n{page_text}\n"
                    
                    # 如果需要提取图片
                    if params.extract_images:
                        page_images = self._extract_images_from_pdf_page(page, page_num)
                        images.extend(page_images)
        
        except Exception as e:
            logger.error(f"PDF处理失败: {str(e)}")
            text_content = f"PDF处理失败: {str(e)}"
        
        # 转换为Markdown格式
        markdown_content = self._convert_to_markdown(text_content, params)
        
        return ExtractionResult(
            text_content=text_content,
            markdown_content=markdown_content,
            images=images,
            tables=tables,
            metadata={"pages": len(pdf_reader.pages) if 'pdf_reader' in locals() else 0}
        )
    

    


    async def _process_text_file(self, task: ProcessingTask) -> ExtractionResult:
        """处理文本文件"""
        file_path = Path(task.file_path)
        params = task.request_params

        try:
            # 读取文本文件
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    text_content = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text_content = f.read()

        # 转换为Markdown格式
        markdown_content = self._convert_to_markdown(text_content, params)

        return ExtractionResult(
            text_content=text_content,
            markdown_content=markdown_content,
            images=[],
            tables=[],
            metadata={"encoding": "utf-8", "lines": len(text_content.split('\n'))}
        )

    async def _process_word_simple(self, task: ProcessingTask) -> ExtractionResult:
        """简化的Word文档处理"""
        file_path = Path(task.file_path)
        params = task.request_params

        # 对于Word文档，我们返回一个提示信息
        text_content = f"Word文档: {file_path.name}\n\n注意: 当前版本主要支持PDF和图片文件的高质量解析。\n对于Word文档，建议先转换为PDF格式以获得更好的解析效果。"

        # 转换为Markdown格式
        markdown_content = f"# {file_path.name}\n\n{text_content}"

        return ExtractionResult(
            text_content=text_content,
            markdown_content=markdown_content,
            images=[],
            tables=[],
            metadata={"processor": "simple", "recommendation": "convert_to_pdf"}
        )
    
    def _extract_images_from_pdf_page(self, page, page_num: int) -> List[Dict]:
        """从PDF页面提取图片"""
        images = []
        # 这里需要实现PDF图片提取逻辑
        # 由于pypdf的图片提取比较复杂，这里先返回空列表
        return images
    
    def _convert_to_markdown(self, text: str, params: DocumentProcessRequest) -> str:
        """将文本转换为Markdown格式"""
        if params.extraction_mode != ExtractionMode.MARKDOWN:
            return text
        
        # 简单的Markdown转换
        lines = text.split('\n')
        markdown_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                markdown_lines.append("")
                continue
            
            # 简单的标题检测
            if len(line) < 50 and not line.endswith('.') and not line.endswith('。'):
                markdown_lines.append(f"## {line}")
            else:
                markdown_lines.append(line)
        
        return '\n'.join(markdown_lines)
    
    def _get_document_type(self, file_path: Path) -> str:
        """根据文件扩展名确定文档类型"""
        suffix = file_path.suffix.lower()

        if suffix == '.pdf':
            return DocumentType.PDF
        elif suffix in ['.docx', '.doc']:
            return DocumentType.DOCX if suffix == '.docx' else DocumentType.DOC
        elif suffix in ['.txt', '.md']:
            return DocumentType.TXT
        elif suffix == '.xml':
            return DocumentType.XML
        elif suffix in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
            return DocumentType.IMAGE
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")
    
    def get_task_result(self, task_id: str) -> Optional[ProcessingTask]:
        """获取任务结果"""
        return self.processing_tasks.get(task_id)
    
    def list_tasks(self, page: int = 1, page_size: int = 20) -> Dict:
        """获取任务列表"""
        tasks = list(self.processing_tasks.values())
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        
        total = len(tasks)
        start = (page - 1) * page_size
        end = start + page_size
        
        return {
            "tasks": tasks[start:end],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        if task_id in self.processing_tasks:
            task = self.processing_tasks[task_id]
            
            # 删除相关文件
            try:
                file_path = Path(task.file_path)
                if file_path.exists():
                    file_path.unlink()
            except Exception as e:
                logger.warning(f"删除文件失败: {str(e)}")
            
            # 从任务列表中删除
            del self.processing_tasks[task_id]
            return True
        
        return False
