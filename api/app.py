# Vercel部署版本的应用入口
from app import app

# Vercel需要这个handler
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == "__main__":
    app.run() 