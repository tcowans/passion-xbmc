
METHODE USE

1. Add required import in your addon.xml
  - exemple 1: ( recommended )
    <requires>
        ...
        <import addon="script.module.dialogaddonscan" version="1.0.0"/>
    </requires>

  - exemple 2:
    import os, sys
    sys.path.append( os.path.join( "MY ADDON PATH", "script.module.dialogaddonscan", "lib" ) )

2. test addon scan demo
    import DialogAddonScan
    #test simple exemple on module DialogAddonScan
    DialogAddonScan.Demo()

3. Normal use addon scan
    import DialogAddonScan
    scan = DialogAddonScan.AddonScan()
    # create dialog
    scan.create( "Tilte" )

    for pct in range( 101 ):
        percent2 = pct
        percent1 = percent2*10
        while percent1 > 100:
            percent1 -= 100
        line2 = "Progress1 [B]%i%%[/B]   |   Progress2 [B]%i%%[/B]" % ( percent1, percent2 )

        # update dialog ( [ int1, int2, line1=str, line2=str ] ) all is optional
        scan.update( percent1, percent2, line2=line2 )
        time.sleep( .25 )

    # close dialog and auto destroy all controls
    scan.close()

4. Scan on background :)
  - Create lib "test_AddonScanInBackground.py" copy exemple "3. Normal use addon scan" or "2. test addon scan demo"

  - In main code or in fonction, add executebuiltin::RunScript
    import os, xbmc
    script = os.path.join( os.getcwd(), "test_AddonScanInBackground.py" )
    xbmc.executebuiltin( "RunScript(%s)" % ( script ) )

   -And now test background :)

5. if your want set dialog position
    ...

6. All Data for custom modif
    ...
