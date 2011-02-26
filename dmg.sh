#!/bin/sh

size=102400
source=../dist/osx_dist_0.5.6.4/
title=TileCutter
backgroundPictureName=tilecutter_dmg_background.png
applicationName=TileCutter.app
finalDMGPath=../dist/
finalDMGName=TileCutter_osx_0.5.6.4.dmg

hdiutil create -srcfolder ${source} -volname "${title}" -fs HFS+ \
      -fsargs "-c c=64,a=16,e=16" -format UDRW -size ${size}k pack.temp.dmg

device=$(hdiutil attach -readwrite -noverify -noautoopen "pack.temp.dmg" | \
         egrep '^/dev/' | sed 1q | awk '{print $1}')

ln -s /Applications /Volumes/${title}/.

bless --folder /Volumes/${title} --openfolder /Volumes/${title}

echo '
    tell application "Finder"
        tell disk "'${title}'"
            open
            tell container window
                set current view to icon view
                set toolbar visible to false
                set statusbar visible to false
                set the bounds to {400, 100, 750, 300}
                set statusbar visible to false
            end tell

            set opts to the icon view options of container window
            tell opts
                set icon size to 128
                set arrangement to not arranged
                set text size to 14
#                set background picture to file "'${backgroundPictureName}'"
            end tell

            # 128px wide for icon, 400px wide total, 144px padding, split into 4 is 36px, 72px, 36px
            # Height just set a reasonable offset from top, say 36px
            set position of item "'${applicationName}'" to {48, 36}
            # 36 + 128 + 72 = 236
            set position of item "Applications" to {224, 36}

            update without registering applications
            delay 5

#            set waitTime to 0
#            set ejectMe to false
#            repeat while ejectMe is false
#                delay 1
#                set waitTime to waitTime + 1
#
#                if (do shell script "[ -f " & dsStore & " ]; echo $?") = "0" then set ejectMe to true
#            end repeat
#            log "waited " & waitTime & " seconds for .DS_STORE to be created."

            close
            open
        end tell
    end tell
' | osascript

chmod -Rf go-w /Volumes/"${title}"
sync
hdiutil detach ${device}
hdiutil convert "./pack.temp.dmg" -format UDZO -imagekey zlib-level=9 -o "${finalDMGPath}${finalDMGName}"
rm -f ./pack.temp.dmg 

