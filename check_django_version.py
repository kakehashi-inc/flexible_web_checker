"""
Djangoバージョン確認スクリプト
"""
import django
import sys

def main():
    """
    Djangoのバージョンと使用しているPythonのバージョンを表示します。
    """
    print(f"Django version: {django.__version__}")
    print(f"Python version: {sys.version}")

if __name__ == "__main__":
    main()
