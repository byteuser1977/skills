#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文档整理技能 - 批量转换主脚本
支持 .doc → .md, .xls → .md, .docx → .md, .xlsx → .md, .ppt → .md, .pptx → .md, .pdf → .md

用法:
  python batch_convert.py --source "源目录" --output "输出目录" [--type doc,xls] [--dry-run]
"""

import argparse
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import sys

def find_libreoffice():
    """自动查找 LibreOffice 安装路径"""
    possible_paths = [
        r"D:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"/usr/bin/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ]
    for path in possible_paths:
        if Path(path).exists():
            return path
    return None

def scan_files(source_dir, file_types):
    """扫描目录中的文件，按类型和目录分组"""
    source = Path(source_dir)
    if not source.exists():
        raise ValueError(f"源目录不存在: {source_dir}")

    all_files = []
    for ft in file_types:
        # 智能匹配：.doc 匹配 .doc 和 .docx；.xls 匹配 .xls 和 .xlsx；.ppt 匹配 .ppt 和 .pptx
        if ft == '.doc':
            all_files.extend(source.rglob('*.doc'))
            all_files.extend(source.rglob('*.docx'))
        elif ft == '.xls':
            all_files.extend(source.rglob('*.xls'))
            all_files.extend(source.rglob('*.xlsx'))
        elif ft == '.ppt':
            all_files.extend(source.rglob('*.ppt'))
            all_files.extend(source.rglob('*.pptx'))
        else:
            all_files.extend(source.rglob(f"*{ft}"))

    # 去重
    all_files = list(set(all_files))

    # 按目录分组
    by_dir = {}
    for f in all_files:
        rel_path = f.relative_to(source)
        parent = str(rel_path.parent)
        if parent not in by_dir:
            by_dir[parent] = []
        by_dir[parent].append(f)

    return by_dir

def convert_docs(by_dir, source_dir, output_dir, soffice_path, temp_root):
    """批量转换 .doc 文件为 .md（LibreOffice 直接）"""
    print(f"\n[步骤 1] Word 文档转换 (.doc → .md)")
    success = 0
    failed = []

    for parent_dir, files in by_dir.items():
        output_subdir = output_dir / parent_dir
        output_subdir.mkdir(parents=True, exist_ok=True)

        # 临时目录（批量转换需要）
        temp_subdir = temp_root / "docs" / parent_dir
        temp_subdir.mkdir(parents=True, exist_ok=True)

        # 复制文件
        for src_file in files:
            dest = temp_subdir / src_file.name
            shutil.copy2(src_file, dest)

        # 批量转换（只对 .doc 文件，.docx 跳过）
        doc_files = [f for f in temp_subdir.glob("*.doc")]
        if doc_files:
            cmd = [soffice_path, "--headless", "--convert-to", "markdown", "--outdir", str(output_subdir), str(temp_subdir / "*.doc")]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    failed.append((parent_dir, f"LibreOffice exit: {result.returncode}"))
            except subprocess.TimeoutExpired:
                failed.append((parent_dir, "Timeout"))

        # 重命名 .markdown → .md
        count = 0
        for md_file in output_subdir.glob("*.markdown"):
            target = md_file.with_suffix('.md')
            if target.exists():
                target.unlink()
            md_file.rename(target)
            count += 1

        success += count
        print(f"  {parent_dir}: {count}/{len(files)}")

        # 清理临时
        shutil.rmtree(temp_subdir, ignore_errors=True)

    return success, failed

def convert_excels(by_dir, source_dir, output_dir, soffice_path, temp_root):
    """批量转换 .xls 文件：.xls → .xlsx → .md（使用 convert-markdown 技能）"""
    print(f"\n[步骤 2] Excel 表格转换 (.xls → .xlsx → .md)")
    success = 0
    failed = []

    for parent_dir, files in by_dir.items():
        output_subdir = output_dir / parent_dir
        output_subdir.mkdir(parents=True, exist_ok=True)

        temp_subdir = temp_root / "excels" / parent_dir
        temp_subdir.mkdir(parents=True, exist_ok=True)

        # 复制
        for src_file in files:
            dest = temp_subdir / src_file.name
            shutil.copy2(src_file, dest)

        # 批量转 .xlsx（只对 .xls 文件）
        xls_files = [f for f in temp_subdir.glob("*.xls")]
        if xls_files:
            cmd = [soffice_path, "--headless", "--convert-to", "xlsx", "--outdir", str(temp_subdir), str(temp_subdir / "*.xls")]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    failed.append((parent_dir, "LibreOffice failed"))
                    shutil.rmtree(temp_subdir, ignore_errors=True)
                    continue
            except subprocess.TimeoutExpired:
                failed.append((parent_dir, "Timeout"))
                shutil.rmtree(temp_subdir, ignore_errors=True)
                continue

        # 对生成的 .xlsx 和原有的 .xlsx 使用 convert-markdown 转换
        xlsx_files = list(temp_subdir.glob("*.xlsx"))
        for xlsx_file in xlsx_files:
            try:
                md_name = xlsx_file.with_suffix('.md').name
                # 调用 convert-markdown 技能
                cmd = [
                    "npx", "skills", "run", "convert-markdown", "convert",
                    "--input", str(xlsx_file),
                    "--output", str(output_subdir / md_name)
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    success += 1
                else:
                    failed.append((str(xlsx_file), f"Exit {result.returncode}: {result.stderr}"))
            except Exception as e:
                failed.append((str(xlsx_file), str(e)))

        shutil.rmtree(temp_subdir, ignore_errors=True)
        print(f"  {parent_dir}: {success} 累计成功")

    return success, failed

def convert_presentations(by_dir, source_dir, output_dir, soffice_path, temp_root):
    """批量转换 .ppt 文件：.ppt → .pptx → .md"""
    print(f"\n[步骤 3] PowerPoint 转换 (.ppt → .pptx → .md)")
    success = 0
    failed = []

    for parent_dir, files in by_dir.items():
        if not files:
            continue
        output_subdir = output_dir / parent_dir
        output_subdir.mkdir(parents=True, exist_ok=True)

        temp_subdir = temp_root / "presentations" / parent_dir
        temp_subdir.mkdir(parents=True, exist_ok=True)

        # 复制
        for src_file in files:
            dest = temp_subdir / src_file.name
            shutil.copy2(src_file, dest)

        # 转 .pptx (只对 .ppt)
        ppt_files = [f for f in temp_subdir.glob("*.ppt")]
        if ppt_files:
            cmd = [soffice_path, "--headless", "--convert-to", "pptx", "--outdir", str(temp_subdir), str(temp_subdir / "*.ppt")]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    failed.append((parent_dir, "LibreOffice failed"))
                    shutil.rmtree(temp_subdir, ignore_errors=True)
                    continue
            except subprocess.TimeoutExpired:
                failed.append((parent_dir, "Timeout"))
                shutil.rmtree(temp_subdir, ignore_errors=True)
                continue

        # 对所有 .pptx 使用 convert-markdown 转换
        pptx_files = list(temp_subdir.glob("*.pptx"))
        for pptx_file in pptx_files:
            try:
                md_name = pptx_file.with_suffix('.md').name
                cmd = [
                    "npx", "skills", "run", "convert-markdown", "convert",
                    "--input", str(pptx_file),
                    "--output", str(output_subdir / md_name)
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    success += 1
                else:
                    failed.append((str(pptx_file), f"Exit {result.returncode}: {result.stderr}"))
            except Exception as e:
                failed.append((str(pptx_file), str(e)))

        shutil.rmtree(temp_subdir, ignore_errors=True)
        print(f"  {parent_dir}: {success} 累计成功")

    return success, failed

def convert_modern(by_dir, suffix, label):
    """使用 convert-markdown 技能转换现代格式（.docx, .xlsx, .pptx）"""
    success = 0

    for parent_dir, files in by_dir.items():
        if not files:
            continue
        output_subdir = output_dir / parent_dir
        output_subdir.mkdir(parents=True, exist_ok=True)

        # 获取该目录下的文件列表
        input_files = [str(f) for f in files]

        # 调用 convert-markdown 技能批量转换
        try:
            # 构建子目录相对路径，用于 output 子目录
            # 这里简化为每个文件单独调用（因为 convert-markdown batch 需要 source/target 目录）
            # 更高效的方式是调用 batch，但需要确保 output_subdir 先创建

            # 方法：为每个文件调用 convert 命令
            for src_file in files:
                cmd = [
                    "npx", "skills", "run", "convert-markdown", "convert",
                    "--input", str(src_file),
                    "--output", str(output_subdir / src_file.with_suffix('.md').name)
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    success += 1
                else:
                    all_failed.append((str(src_file), suffix, f"Exit {result.returncode}: {result.stderr}"))

        except Exception as e:
            all_failed.append((parent_dir, suffix, str(e)))

        print(f"  {label} {parent_dir}: {success} 累计成功")

    return success

def convert_pdfs(by_dir, output_dir):
    """批量转换 .pdf 文件 - 使用 convert-markdown 技能"""
    print(f"\n[步骤 4] PDF 文档转换 (.pdf → .md)")
    success = 0
    failed = []

    for parent_dir, files in by_dir.items():
        if not files:
            continue
        output_subdir = output_dir / parent_dir
        output_subdir.mkdir(parents=True, exist_ok=True)

        for src_file in files:
            try:
                cmd = [
                    "npx", "skills", "run", "convert-markdown", "convert",
                    "--input", str(src_file),
                    "--output", str(output_subdir / src_file.with_suffix('.md').name)
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    success += 1
                else:
                    failed.append((str(src_file), f"Exit {result.returncode}: {result.stderr}"))
            except Exception as e:
                failed.append((str(src_file), str(e)))

        print(f"  {parent_dir}: {success} 累计成功")

    return success, failed

def main():
    parser = argparse.ArgumentParser(description="批量文档转换工具")
    parser.add_argument("--source", required=True, help="源目录路径")
    parser.add_argument("--output", default="./output", help="输出目录路径")
    parser.add_argument("--type", default="doc,xls,docx,xlsx,ppt,pptx,pdf", help="处理的文件类型（逗号分隔）")
    parser.add_argument("--soffice-path", help="LibreOffice soffice.exe 路径（自动检测）")
    parser.add_argument("--dry-run", action="store_true", help="仅模拟，不实际转换")
    parser.add_argument("--log-file", default="conversion.log", help="日志文件路径")
    args = parser.parse_args()

    # 初始化
    source_dir = Path(args.source).resolve()
    output_dir = Path(args.output).resolve()
    temp_root = Path("./temp_batch").resolve()

    if temp_root.exists():
        shutil.rmtree(temp_root)
    temp_root.mkdir(parents=True, exist_ok=True)

    # 查找 LibreOffice
    soffice_path = args.soffice_path or find_libreoffice()
    if not soffice_path or not Path(soffice_path).exists():
        print("❌ 未找到 LibreOffice，请安装或指定路径")
        sys.exit(1)

    print("="*60)
    print("文档批量转换工具")
    print(f"源目录: {source_dir}")
    print(f"输出目录: {output_dir}")
    print(f"LibreOffice: {soffice_path}")
    print("="*60)

    # 扫描文件
    file_types = [f".{t.strip()}" for t in args.type.split(',')]
    by_dir = scan_files(source_dir, file_types)

    total_files = sum(len(files) for files in by_dir.values())
    print(f"\n扫描结果: {total_files} 个文件，{len(by_dir)} 个子目录")

    if args.dry_run:
        print("\n[Dry Run] 不执行转换，仅显示统计")
        for parent, files in by_dir.items():
            counts = {}
            for f in files:
                ext = f.suffix.lower()
                counts[ext] = counts.get(ext, 0) + 1
            print(f"  {parent}: {counts}")
        return

    # 分离不同类型
    doc_files_by_dir = {p: [f for f in fs if f.suffix.lower() == '.doc'] for p, fs in by_dir.items()}
    xls_files_by_dir = {p: [f for f in fs if f.suffix.lower() == '.xls'] for p, fs in by_dir.items()}
    docx_files_by_dir = {p: [f for f in fs if f.suffix.lower() == '.docx'] for p, fs in by_dir.items()}
    xlsx_files_by_dir = {p: [f for f in fs if f.suffix.lower() == '.xlsx'] for p, fs in by_dir.items()}
    ppt_files_by_dir = {p: [f for f in fs if f.suffix.lower() == '.ppt'] for p, fs in by_dir.items()}
    pptx_files_by_dir = {p: [f for f in fs if f.suffix.lower() == '.pptx'] for p, fs in by_dir.items()}
    pdf_files_by_dir = {p: [f for f in fs if f.suffix.lower() == '.pdf'] for p, fs in by_dir.items()}

    total_success = 0
    all_failed = []

    # 1. 转换 .doc
    if any(doc_files_by_dir.values()):
        success, failed = convert_docs(doc_files_by_dir, source_dir, output_dir, soffice_path, temp_root)
        total_success += success
        all_failed.extend([(f, "doc", err) for f, err in failed])

    # 2. 转换 .xls
    if any(xls_files_by_dir.values()):
        success, failed = convert_excels(xls_files_by_dir, source_dir, output_dir, soffice_path, temp_root)
        total_success += success
        all_failed.extend([(f, "xls", err) for f, err in failed])

    # 3. 转换 .ppt
    if any(ppt_files_by_dir.values()):
        success, failed = convert_presentations(ppt_files_by_dir, source_dir, output_dir, soffice_path, temp_root)
        total_success += success
        all_failed.extend([(f, "ppt", err) for f, err in failed])

    # 4. 现代格式（直接 MarkItDown）
    if any(docx_files_by_dir.values()):
        success = convert_modern(docx_files_by_dir, '.docx', "DOCX")
        total_success += success

    if any(xlsx_files_by_dir.values()):
        success = convert_modern(xlsx_files_by_dir, '.xlsx', "XLSX")
        total_success += success

    if any(pptx_files_by_dir.values()):
        success = convert_modern(pptx_files_by_dir, '.pptx', "PPTX")
        total_success += success

    # 5. PDF 转换
    if any(pdf_files_by_dir.values()):
        success, failed = convert_pdfs(pdf_files_by_dir, output_dir)
        total_success += success
        all_failed.extend([(f, "pdf", err) for f, err in failed])

    # 清理
    shutil.rmtree(temp_root, ignore_errors=True)

    # 报告
    print(f"\n" + "="*60)
    print("转换完成")
    print(f"总成功: {total_success}/{total_files}")
    print(f"输出目录: {output_dir}")
    print("="*60)

    # 错误日志
    if all_failed:
        log_path = Path(args.log_file)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n# 转换失败记录 ({datetime.now()})\n")
            for file_path, typ, err in all_failed:
                f.write(f"- [{typ}] {file_path}: {err}\n")
        print(f"失败记录: {log_path}")

if __name__ == '__main__':
    main()
