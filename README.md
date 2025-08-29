## Wallpaper_Engine_Tools
用于管理Wallpaper Engine壁纸的工具，python+PySide6

### Project setup

```
pip install pyinstaller
```

### Compiles for development

```
pyinstaller -D --windowed -n "Wallpaper_Engine_Tools" --add-binary "./RePKG.exe;." app.py
pyinstaller --onefile -n "Wallpaper_Engine_Tools" --add-binary "./RePKG.exe;." app.py
pyinstaller Wallpaper_Engine_Tools.spec
```



### 功能开发

> setam安装位置获取
>
> > ~~win注册表~~
> >
> > 快捷方式拖入
>
> wallpaper engine安装位置获取
>
> > ~~win注册表~~
> >
> > 快捷方式拖入
>
> wallpaper engine - config
>
> > 识别
> >
> > 订阅获取
> >
> > 项目引用必须物品关联
> >
> > 取消订阅留存
> >
> > > 查询
> > >
> > > 删除
>
> 订阅展示
>
> > ~~图文列表~~
> >
> > 图文拆分
> >
> > 筛选
> >
> > 容量
>
> 备份订阅
>
> > 标题修改
> >
> > 分类整理
>
> 应用解压
>
> > 标记导入管理
> >
> > 列表管理
> >
> > > 展示
> > >
> > > 删除
>
> config打包排除
>
> 硬盘瘦身
>
> > ~~软链接~~
> >
> > NAS快捷方式目录
> >
> > 生成选择改版 - 多标签调用，含已生成
>
> RePKG
>
> > ~~场景图片提取~~
> > 拖入提取

