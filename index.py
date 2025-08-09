import os
import sys

# 确保Vercel环境变量
os.environ['VERCEL'] = '1'

try:
    from app import app
    
    # Vercel需要这个函数
    def application(environ, start_response):
        return app(environ, start_response)
    
    # 导出给Vercel
    app = app
    
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)

# 如果直接运行此文件  
if __name__ == "__main__":
    app.run(debug=True) 