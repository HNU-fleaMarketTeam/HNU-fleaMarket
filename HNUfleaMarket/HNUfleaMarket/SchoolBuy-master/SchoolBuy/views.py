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
