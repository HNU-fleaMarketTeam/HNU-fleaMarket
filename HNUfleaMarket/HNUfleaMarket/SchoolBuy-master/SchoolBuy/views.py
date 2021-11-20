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
#修改密码
def change_passwd(request):
    if request.method != 'POST':
        return HttpResponseRedirect('/me/edit/')
    else:
        profile = UserProfile.objects.get(User=request.user)
        form = UserMessage(instance=profile)
        pass_form = ChangePasswd(request.POST)
        passwd = request.POST.get('old_passwd',None)
        name = request.user.username
        user = auth.authenticate(username=name,password=passwd)
        email_form = BindEmailForm()
        if not user:
            pass_form.add_error('old_passwd','原密码错误！')
            return render(request, 'SchoolBuy/ChangeMyself.html', {'profile': profile,
                                                                   'form': form,
                                                                   'user': request.user,
                                                                   'email_form': email_form,
                                                                   'pass_form':pass_form,
                                                                   })
        if pass_form.is_valid():
            user.set_password(pass_form.cleaned_data['new_passwd'])
            user.save()
            auth.logout(request)
            request.session.clear()
            return render(request, "SchoolBuy/doing_success.html", {'mes': '修改密码'})
    return render(request, 'SchoolBuy/ChangeMyself.html', {'profile': profile,
                                                           'form': form,
                                                           'user': request.user,
                                                           'email_form': email_form,
                                                           'pass_form': pass_form})

@csrf_exempt
def verifi_email(request):
    code = request.GET.get('code',None)
    code = UserProfile.objects.filter(EmailCode=code).first()
    if not code:
        raise Http404()
    if (datetime.datetime.now()-code.EmailCodeTime).seconds >= 3600*24:
        return HttpResponse('验证链接已经过期，请重新生成！')
    else:
        user = code.User
        temp_email = base64.b64decode(code.EmailCode[:-24].encode('utf8'))
        user.email = temp_email
        user.save()
        code.EmailCode = None
        code.EmailCodeTime = None
        code.save()
        return HttpResponse('激活成功！')

@login_required
def del_email(request):
    user = request.user
    user.email=''
    user.save()
    return HttpResponseRedirect('/me/edit/')

def send_passwd_mail(mail,profile):
    str = (base64.b64encode(mail.encode('utf8'))).decode('utf8')
    str += ''.join(random.sample(string.ascii_letters + string.digits, 24))
    profile.PasswdCode = str
    profile.PasswdCodeTime = datetime.datetime.now()
    profile.save()
    url = '请点击这个链接来重新设定您的密码(24小时内有效)\n' + settings.HOST_URL_ADDRESS + '/comm/passwd/?code='+str
    send_mail('重置密码',url,settings.DEFAULT_FROM_EMAIL,[mail,],fail_silently=False)

    #输入邮箱找回密码
def find_passwd(request):
    if request.method == 'GET':
        form = FindPasswdForm()

    else:
        form = FindPasswdForm(request.POST)
        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data['email'])
            profile = UserProfile.objects.get(User=user)
            if profile.PasswdCodeTime and (datetime.datetime.now() - profile.PasswdCodeTime).seconds <= 1800 :
                form.add_error('email','已于'+profile.PasswdCodeTime.strftime('%Y-%m-%d %H:%M:%S')+
                               '发送了重置邮件，半小时内无法再次发送')

            else:
                send_passwd_mail(form.cleaned_data['email'],profile)
                return HttpResponse('已向你发送了重置密码链接，快去邮箱查看吧！')
    return render(request,'SchoolBuy/ForgetPasswd.html',{'form':form})

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
