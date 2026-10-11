



if __name__ == "__main__":
  print(" this is main file : my_fun.py")

else:
    # print("this file %s is not main file"%__file__)
    def my_len(s):
        cnt=0
        for i in s:
            cnt+=1
        return cnt
    
    def len_alwayszero(s):
        return 0    
    
    def intadd(a,b):
        #以上的是形参
        # 形参要开空间，实参不需要开空间
        return a+b
    

    