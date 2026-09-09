#(2)imageio 库的应用
import imageio , os , numpy
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image

#指定：原图片文件的路径及文件名
src_file_name   = r"homework/py实验/67/620160d19367e1392c4fcfb6e1f85ed0.jpg"
src_file = os.getcwd() + '\\' + src_file_name

src_pic = imageio.imread( src_file )              #读取图片
print("图片的数据类型：" , src_pic.dtype )        #获取图片数据类型

src_pic_shape = src_pic.shape                     #获取图片大小
print("(图片大小，通道数)：" , src_pic_shape )

#修改图片颜色并保存
##imageio.imwrite("src_mc.jpg" , src_src *[1 , 0.5 ,0.5 ] )   #不同版本的语法格式差异！！！  
imageio.imwrite( r"homework/py实验/67/实验06_imageio_src_mc.jpg" , ( src_pic*[1,0.5,0.5]).astype(numpy.uint8) )

#修改图片分辨率并保存
imageio.imwrite( r"homework/py实验/67/实验06_imageio_src_ms.jpg" , numpy.array( Image.fromarray( src_pic ).resize((120 , 70))))

#裁剪图片并保存
imageio.imwrite( r"homework/py实验/67/实验06_imageio_src_mi.jpg" , src_pic[50:130 , 100:240])

'''-------------绘制图片-------------'''

plt.figure( )

plt.subplot( 2 , 2 , 1 )
src_jpg1 = mpimg.imread( r"homework/py实验/67/620160d19367e1392c4fcfb6e1f85ed0.jpg" )   #读取图片
plt.imshow( src_jpg1 )                                #显示图片
plt.axis( 'off' )                                   #绘图时：隐藏坐标轴

plt.subplot( 2 , 2 ,2 )
src_jpg2 = mpimg.imread( r"homework/py实验/67/实验06_imageio_src_mc.jpg" )
plt.imshow( src_jpg2 )
plt.axis('on')                                      #绘图时：显示坐标轴

plt.subplot( 2 , 2 , 3 )
src_jpg3 = mpimg.imread( r"homework/py实验/67/实验06_imageio_src_ms.jpg" )
plt.imshow( src_jpg3 )
plt.axis('on' )

plt.subplot( 2 , 2 , 4)
src_jpg4 = mpimg.imread( r"homework/py实验/67/实验06_imageio_src_mi.jpg")
plt.imshow(src_jpg4)
plt.axis('on')
plt.show()

