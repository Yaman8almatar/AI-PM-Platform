import sys
import os

# هذا السطر يضيف مجلد backend تلقائياً لمسار بايثون عند تشغيل pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))