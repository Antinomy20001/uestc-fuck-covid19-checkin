# uestc-fuck-covid19-checkin

设置一个透明代理捕获登录你电eportal时的cookie，然后帮你keepalive这个cookie并帮你打卡的一个工具。

安装好docker和docker-compose后

```docker-compose up -d```

就可以了，具体是监听哪个端口可以在```docker-compose.yml```中修改

然后自己想办法让登录时走这个HTTP透明代理，推荐SwitchyOmega设置Auto Switch，网址通配符：```http://eportal.uestc.edu.cn/jsonp/getUserFirstLogin*```，让走挂好的HTTP代理。

然后登录一次就行了。

代码是随便写的，十分的Dirty