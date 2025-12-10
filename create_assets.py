from PIL import Image, ImageDraw, ImageFont
import os

# 创建assets目录
os.makedirs('assets', exist_ok=True)

# 创建图标 (512x512)
icon = Image.new('RGB', (512, 512), color='#2196F3')
draw = ImageDraw.Draw(icon)
# 绘制相机图标
draw.ellipse((100, 100, 412, 412), fill='white', outline='#1976D2', width=10)
draw.ellipse((156, 156, 356, 356), fill='#2196F3')
draw.rectangle((246, 200, 266, 312), fill='white')
icon.save('assets/icon.png')

# 创建启动画面 (1080x1920)
splash = Image.new('RGB', (1080, 1920), color='#2196F3')
draw = ImageDraw.Draw(splash)
# 添加渐变效果
for i in range(1920):
    r = int(33 * (1 - i/1920) + 25 * (i/1920))
    g = int(150 * (1 - i/1920) + 118 * (i/1920))
    b = int(243 * (1 - i/1920) + 210 * (i/1920))
    draw.line([(0, i), (1080, i)], fill=(r, g, b))

# 添加文字（如果系统有中文字体可以使用）
try:
    font = ImageFont.truetype("/system/fonts/DroidSansFallback.ttf", 72)
except:
    font = ImageFont.load_default()

draw.text((540, 960), "物品记录器", fill='white', font=font, anchor='mm')
splash.save('assets/presplash.png')

print("资源文件已创建在 assets/ 目录")
