from app import app

# Vercel需要这个作为入口点
def handler(request):
    return app

# 如果直接运行此文件
if __name__ == "__main__":
    app.run(debug=True) 