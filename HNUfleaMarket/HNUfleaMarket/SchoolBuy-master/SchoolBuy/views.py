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

#登录
def login(request):
    if request.method == 'POST':
        name = request.POST.get('username', '')
        passwd = request.POST.get('password', '')
        user = auth.authenticate(username=name, password=passwd)
        if user is not None and user.is_active:
            auth.login(request, user)
            profile = UserProfile.objects.get(User=user)
            request.session['nick'] = profile.Nick
            request.session['avatar'] = profile.Avatar
            return HttpResponseRedirect('/')

        else:
            return render(request, 'SchoolBuy/Login.html', {'error': '用户名和密码不匹配！'})

    else:
        return render(request, 'SchoolBuy/Login.html')

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

@login_required
#绑定邮箱
def bind_email(request):
    if request.method != 'POST':
        return HttpResponseRedirect('/me/edit/')

    form = UserMessage()
    pass_form = ChangePasswd()
    profile = UserProfile.objects.get(User=request.user)
    if request.user.email:
        return HttpResponse("error!重复绑定")
    user = request.user
    email_form = BindEmailForm(request.POST)
    if profile.EmailCodeTime and (datetime.datetime.now()-profile.EmailCodeTime).seconds <= 3600:
        email_form.add_error('email','1小时内不能重复发送激活邮件')
        return render(request, 'SchoolBuy/ChangeMyself.html',
                      {'profile': profile, 'form': form,
                       'pass_form': pass_form, 'email_form': email_form,
                       'user': request.user})

    else:
        if email_form.is_valid():
            send_required_mail(email_form.cleaned_data['email'],profile)
            return HttpResponseRedirect('/me/edit/')

        return render(request, 'SchoolBuy/ChangeMyself.html',
                      {'profile': profile, 'form': form,
                       'pass_form': pass_form, 'email_form': email_form,
                       'user': request.user})


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
