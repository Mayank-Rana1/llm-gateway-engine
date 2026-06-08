class student:
    pass

def sub():
    a="name"
    b="subname"
    c="lastname"
    return a,b,c

def my_main():
    a,b=sub()
    print(f"first:{a[0]} and second:{b[1]} and third:{b[0]}")

if __name__=="__main__":
    my_main()