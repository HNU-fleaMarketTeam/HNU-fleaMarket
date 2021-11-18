#注册
def register(request):
    code_err = False
    if request.method == 'POST':
        form = Register(request.POST)

        if request.POST.get('code', ' ') != request.session.get('check_code', None):
            code_err = True

        else:
            if form.is_valid():  # 判断是否合法
                user = User.objects.create_user(username=form.cleaned_data['username']
                                                , password=form.cleaned_data['passwd'])
                user.date_joined = datetime.datetime.now()
                user.save()
                all_user = UserProfile()
                all_user.User = user
                all_user.Nick = user.username
                all_user.save()
                send_mail('用户注册',
                          '用户名：'+form.cleaned_data['username']+'\n密码：'+form.cleaned_data['passwd'],
                          settings.DEFAULT_FROM_EMAIL,
                         [settings.ADMIN_EMAIL,], fail_silently=False)
                return HttpResponseRedirect('/')
    else:
        form = Register()
    return render(request, 'SchoolBuy/Register.html', {'form': form,'code_err':code_err})

@login_required
#用户个人信息
def user_message(request):
    user = request.user
    profile = UserProfile.objects.get(User=user)
    #包含下架商品
    goods = GoodsMessage.objects.filter(Owner=user)

    #系统通知个数
    log = len(GoodsLog.objects.filter(To = user,Readed=False))

    return render(request,'SchoolBuy/MyMessage.html', {'log':log,'profile': profile, 'goods': goods})

#保存头像
def savehead(pic):
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'head')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'head'))
    randname = ''.join(random.sample(string.ascii_letters + string.digits, 24))
    randname += '.' + pic.name.split('.')[-1]
    full_path = os.path.join(settings.MEDIA_ROOT, 'head', randname)
    fd = open(full_path, 'wb+')
    for chunks in pic.chunks():
        fd.write(chunks)
    fd.close()
    if (filetype(full_path) == 'unknown'):
        os.remove(full_path)
        return None
    else:
        nn = creat_head(full_path)
        os.remove(full_path)
        return nn
