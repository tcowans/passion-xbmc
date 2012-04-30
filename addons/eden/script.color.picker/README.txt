How to pick color:
RunScript(script.color.picker,Built-In[,extra])

Built-In for Skin:
 - Skin.SetString(MyPrettyColor[,default_color])

Built-In for Add-on:
 - Addon('MyAddonId').setSetting('MyPrettyColor'[,'default_color'])

Note: Built-In option 'default_color' will be used, if the user does not choose a color.

For skin example:
RunScript(script.color.picker,Skin.SetString(MyPrettyColor,FFEB9E17))

For Add-on example:
RunScript(script.color.picker,Addon('script.color.picker').setSetting('MyPrettyColor'))



Extra params: ( join params with & )
 - Start=PickColorOnScreen (if you want pick color of current Screen)
 - SetStringInRealTime=true (if you want view change color in real time. only for Skin Built-In)
 - Transparency&Min=0&Max=100 (if you want ajust only transparency)

For example:
RunScript(script.color.picker,Built-In,Start=PickColorOnScreen)
RunScript(script.color.picker,Built-In,Start=PickColorOnScreen&SetStringInRealTime=true)

RunScript(script.color.picker,Built-In,SetStringInRealTime=true)

RunScript(script.color.picker,Built-In,Transparency&Min=20&Max=90)
RunScript(script.color.picker,Built-In,Transparency&Min=20&Max=90&SetStringInRealTime=true)
