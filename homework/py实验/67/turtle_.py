import turtle

# 创建画布
screen = turtle.Screen()
screen.bgcolor("black")

# 创建画笔
t = turtle.Turtle()
t.speed(0)
t.width(2)

# 颜色列表
colors = ["red", "orange", "yellow", "green", "cyan", "blue", "purple"]

# 绘制另类螺旋图案
for i in range(180):
    t.color(colors[i % len(colors)])
    t.forward(i * 2)
    t.right(61)
    t.circle(i / 3)

# 隐藏画笔
t.hideturtle()

# 保持窗口显示
turtle.done()