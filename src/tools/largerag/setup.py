"""
LargeRAG工具安装配置
基于LlamaIndex的大规模文献RAG系统
"""

from setuptools import setup, find_packages
import os

# 读取requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
        return requirements

# 读取README（如果存在）
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "LargeRAG - 基于LlamaIndex的大规模文献RAG系统"

setup(
    name="largerag",
    version="0.1.0",
    description="基于LlamaIndex的大规模文献RAG系统",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="DES System Design Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=read_requirements(),
    include_package_data=True,
    package_data={
        "largerag": [
            "config/*.yaml",
            "config/*.yml",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "largerag=largerag.cli:main",
        ],
    },
)