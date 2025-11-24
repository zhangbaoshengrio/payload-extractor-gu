#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Payload Dumper GUI
一个图形界面工具，用于从 Android payload.bin 文件中提取指定的分区镜像
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import sys
import threading
import json

class PayloadExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Payload 分区提取工具")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # 变量
        self.payload_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.partition_vars = {}
        
        # 常见的分区列表
        self.common_partitions = [
            "boot", "init_boot", "vendor_boot", "recovery",
            "system", "system_ext", "product", "vendor",
            "odm", "vbmeta", "vbmeta_system", "dtbo",
            "super", "userdata", "metadata"
        ]
        
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 1. Payload.bin 文件选择
        ttk.Label(main_frame, text="Payload 文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.payload_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        ttk.Button(main_frame, text="浏览...", command=self.browse_payload).grid(row=0, column=2, pady=5)
        
        # 2. 输出目录选择
        ttk.Label(main_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        ttk.Button(main_frame, text="浏览...", command=self.browse_output).grid(row=1, column=2, pady=5)
        
        # 3. 分区列表按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="扫描分区", command=self.scan_partitions).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="全选", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消全选", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="常用分区", command=self.select_common).pack(side=tk.LEFT, padx=5)
        
        # 4. 分区勾选框区域
        partition_label = ttk.Label(main_frame, text="选择要提取的分区:")
        partition_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        # 创建可滚动的分区列表框架
        partition_frame = ttk.Frame(main_frame)
        partition_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(4, weight=1)
        
        # 添加滚动条
        canvas = tk.Canvas(partition_frame, height=200)
        scrollbar = ttk.Scrollbar(partition_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 初始显示常见分区
        self.display_partitions(self.common_partitions)
        
        # 5. 提取按钮
        extract_frame = ttk.Frame(main_frame)
        extract_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        self.extract_button = ttk.Button(extract_frame, text="开始提取", command=self.start_extraction)
        self.extract_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(extract_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # 6. 日志输出区域
        log_label = ttk.Label(main_frame, text="执行日志:")
        log_label.grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(7, weight=2)
        
    def browse_payload(self):
        """选择 payload.bin 文件"""
        filename = filedialog.askopenfilename(
            title="选择 payload.bin 文件",
            filetypes=[("Payload 文件", "*.bin"), ("所有文件", "*")]
        )
        if filename:
            self.payload_path.set(filename)
            self.log(f"已选择 payload 文件: {filename}")
            
    def browse_output(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_path.set(directory)
            self.log(f"已选择输出目录: {directory}")
            
    def display_partitions(self, partitions):
        """显示分区勾选框"""
        # 清空现有的勾选框
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.partition_vars.clear()
        
        # 创建新的勾选框（3列布局）
        for i, partition in enumerate(partitions):
            var = tk.BooleanVar()
            self.partition_vars[partition] = var
            
            row = i // 3
            col = i % 3
            
            cb = ttk.Checkbutton(self.scrollable_frame, text=partition, variable=var)
            cb.grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
            
    def scan_partitions(self):
        """扫描 payload.bin 中的所有分区"""
        payload = self.payload_path.get()
        
        if not payload:
            messagebox.showwarning("警告", "请先选择 payload.bin 文件！")
            return
            
        if not os.path.exists(payload):
            messagebox.showerror("错误", "选择的 payload.bin 文件不存在！")
            return
        
        self.log("正在扫描分区列表...")
        
        try:
            # 使用 payload-dumper-go -l 列出所有分区
            result = subprocess.run(
                ["payload-dumper-go", "-l", payload],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 解析输出获取分区名称
                partitions = []
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('[') and not line.startswith('Processing'):
                        # 简单解析，实际格式可能需要调整
                        if ':' in line:
                            partition = line.split(':')[0].strip()
                            if partition:
                                partitions.append(partition)
                
                if partitions:
                    self.display_partitions(sorted(set(partitions)))
                    self.log(f"扫描完成，找到 {len(partitions)} 个分区")
                else:
                    self.log("未能解析分区列表，使用默认分区列表")
                    self.display_partitions(self.common_partitions)
            else:
                self.log(f"扫描失败: {result.stderr}")
                messagebox.showerror("错误", f"扫描分区失败:\n{result.stderr}")
                
        except FileNotFoundError:
            self.log("错误: 未找到 payload-dumper-go 命令")
            messagebox.showerror("错误", "未找到 payload-dumper-go 工具！\n请确保已安装并添加到系统 PATH 中。")
        except subprocess.TimeoutExpired:
            self.log("扫描超时")
            messagebox.showerror("错误", "扫描超时！")
        except Exception as e:
            self.log(f"扫描出错: {str(e)}")
            messagebox.showerror("错误", f"扫描出错:\n{str(e)}")
            
    def select_all(self):
        """全选所有分区"""
        for var in self.partition_vars.values():
            var.set(True)
        self.log("已全选所有分区")
        
    def deselect_all(self):
        """取消全选"""
        for var in self.partition_vars.values():
            var.set(False)
        self.log("已取消全选")
        
    def select_common(self):
        """选择常用分区"""
        common = ["boot", "init_boot", "vendor_boot", "recovery", "vbmeta", "dtbo"]
        for partition, var in self.partition_vars.items():
            var.set(partition in common)
        self.log("已选择常用分区: " + ", ".join(common))
        
    def log(self, message):
        """输出日志"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        
    def start_extraction(self):
        """开始提取"""
        payload = self.payload_path.get()
        output = self.output_path.get()
        
        # 验证输入
        if not payload:
            messagebox.showwarning("警告", "请选择 payload.bin 文件！")
            return
            
        if not output:
            messagebox.showwarning("警告", "请选择输出目录！")
            return
            
        if not os.path.exists(payload):
            messagebox.showerror("错误", "payload.bin 文件不存在！")
            return
            
        # 获取选中的分区
        selected = [name for name, var in self.partition_vars.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("警告", "请至少选择一个分区！")
            return
            
        # 创建输出目录
        os.makedirs(output, exist_ok=True)
        
        # 在新线程中执行提取
        thread = threading.Thread(target=self.extract_partitions, args=(payload, output, selected))
        thread.daemon = True
        thread.start()
        
    def extract_partitions(self, payload, output, partitions):
        """执行提取操作"""
        self.extract_button.config(state='disabled')
        self.log("=" * 60)
        self.log(f"开始提取 {len(partitions)} 个分区...")
        self.log(f"输入文件: {payload}")
        self.log(f"输出目录: {output}")
        self.log(f"选中分区: {', '.join(partitions)}")
        self.log("=" * 60)
        
        success_count = 0
        fail_count = 0
        
        for partition in partitions:
            self.log(f"\n正在提取: {partition}")
            
            try:
                # 构建命令
                cmd = [
                    "payload-dumper-go",
                    "-p", partition,
                    "-o", output,
                    payload
                ]
                
                # 执行命令
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )
                
                if result.returncode == 0:
                    self.log(f"✓ {partition} 提取成功")
                    success_count += 1
                else:
                    self.log(f"✗ {partition} 提取失败: {result.stderr}")
                    fail_count += 1
                    
            except FileNotFoundError:
                self.log(f"✗ 错误: 未找到 payload-dumper-go 命令")
                messagebox.showerror("错误", "未找到 payload-dumper-go 工具！\n请确保已安装并添加到系统 PATH 中。")
                break
            except subprocess.TimeoutExpired:
                self.log(f"✗ {partition} 提取超时")
                fail_count += 1
            except Exception as e:
                self.log(f"✗ {partition} 提取出错: {str(e)}")
                fail_count += 1
                
        # 完成
        self.log("\n" + "=" * 60)
        self.log(f"提取完成！成功: {success_count}, 失败: {fail_count}")
        self.log("=" * 60)
        
        self.extract_button.config(state='normal')
        
        if success_count > 0:
            messagebox.showinfo("完成", f"提取完成！\n成功: {success_count}\n失败: {fail_count}\n\n文件保存在:\n{output}")

def main():
    root = tk.Tk()
    app = PayloadExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
