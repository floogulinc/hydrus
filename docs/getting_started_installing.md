---
title: installing and updating  
---

If any of this is confusing, a simpler guide is [here](https://github.com/Zweibach/text/blob/master/Hydrus/Hydrus%20Help%20Docs/00_tableOfContents.md), and some video guides are [here](https://github.com/CuddleBear92/Hydrus-guides)!

## downloading

You can get the latest release at [my github releases page](https://github.com/hydrusnetwork/hydrus/releases).

I try to release a new version every Wednesday by 8pm EST and write an accompanying post on [my tumblr](http://hydrus.tumblr.com/) and a Hydrus Network General thread on [8chan.moe /t/](https://8chan.moe/t/catalog.html).

## installing

!!! warning ""
    The hydrus releases are 64-bit only. If you are a python expert, there is the slimmest chance you'll be able to get it running from source on a 32-bit machine, but it would be easier just to find a newer computer to run it on.

=== "Windows"

    *   If you want the easy solution, download the .exe installer. Run it, hit ok several times.
    *   If you know what you are doing and want a little more control, get the .zip. Don't extract it to Program Files unless you are willing to run it as administrator every time (it stores all its user data inside its own folder). You probably want something like D:\\hydrus.
    *   _Note if you run <Win10, you may need [Visual C++ Redistributable for Visual Studio 2015](https://www.microsoft.com/en-us/download/details.aspx?id=48145), if you don't already have it for vidya. If you run Win7, you will need some/all core OS updates released before 2017._
    *   If you use Windows 10 N (a version of Windows without some media playback features), you will likely need the 'Media Feature Pack'. There have been several versions of this, so it may best found by searching for the latest version or hitting Windows Update, but otherwise check [here](https://support.microsoft.com/en-us/help/3145500/media-feature-pack-list-for-windows-n-editions).

=== "macOS"

    *   Get the .dmg App. Open it, drag it to Applications, and check the readme inside.

=== "Linux"

    *   Get the .tag.gz. Extract it somewhere useful and create shortcuts to 'client' and 'server' as you like. The build is made on Ubuntu, so if you run something else, compatibility is hit and miss.
    *   If you use Arch Linux, you can check out the AUR package a user maintains [here](https://aur.archlinux.org/packages/hydrus/).
    *   If you have problems running the Ubuntu build, users with some python experience generally find running from source works well.
    *   You might need to get 'libmpv1' to get mpv working and playing video/audio. This is the mpv library, not the player. Check help->about to see if it is available--if not, see if you can get it with _apt_.
    *   You can also try [running the Windows version in wine](wine.md).

=== "From Source"

    *   If you have some python experience, you can [run from source](running_from_source.md).

By default, hydrus stores all its data—options, files, subscriptions, _everything_—entirely inside its own directory. You can extract it to a usb stick, move it from one place to another, have multiple installs for multiple purposes, wrap it all up inside a truecrypt volume, whatever you like. The .exe installer writes some unavoidable uninstall registry stuff to Windows, but the 'installed' client itself will run fine if you manually move it.

!!! info "For macOS users"
    The Hydrus App is **non-portable** and puts your database in ~/Library/Hydrus (i.e. /Users/\[You\]/Library/Hydrus). You can update simply by replacing the old App with the new, but if you wish to backup, you should be looking at ~/Library/Hydrus, not the App itself.

## running

To run the client:

=== "Windows"

    *   For the installer, run the Start menu shortcut it added.
    *   For the extract, run 'client.exe' in the base directory, or make a shortcut to it.

=== "macOS"

    *   Run the App you installed.

=== "Linux"

    *   Run the 'client' executable in the base directory. You may be able to double-click it, otherwise you are talking './client' from the terminal.
    *   If you experience virtual memory crashes, please review [this thorough guide](Fixing_Hydrus_Random_Crashes_Under_Linux.md) by a user.

## updating

!!! danger
    Hydrus is imageboard-tier software, wild and fun but unprofessional. It is written by one Anon spinning a lot of plates. Mistakes happen from time to time, usually in the update process. There are also no training wheels to stop you from accidentally overwriting your whole db if you screw around. Be careful when updating. Make backups beforehand!

**Hydrus does not auto-update. It will stay the same version unless you download and install a new one.**

Although I put out an new version every week, you can update far less often if you want. The client keeps to itself, so if it does exactly what you want and a new version does nothing you care about, you can just leave it. Other users enjoy updating every week, simply because it makes for a nice schedule. Others like to stay a week or two behind what is current, just in case I mess up and cause a temporary bug in something they like.

A user has written a longer and more formal guide to updating, and information on the 334->335 step [here](update_guide.rtf).

The update process:

*   If the client is running, close it!
*   If you maintain a backup, run it now!
*   If you use the installer, just download the new installer and run it. It should detect where the last install was and overwrite everything automatically.
*   If you extract, then just extract the new version right on top of your current install and overwrite manually.
*   Start your client or server. It may take a few minutes to update its database. I will say in the release post if it is likely to take longer.

Unless the update specifically disables or reconfigures something, all your files and tags and settings will be remembered after the update.

Releases typically need to update your database to their version. New releases can retroactively perform older database updates, so if the new version is v255 but your database is on v250, you generally only need to get the v255 release, and it'll do all the intervening v250->v251, v251->v252, etc... update steps in order as soon as you boot it. If you need to update from a release more than, say, ten versions older than current, see below. You might also like to skim the release posts or [changelog](changelog.html) to see what is new.

Clients and servers of different versions can usually connect to one another, but from time to time, I make a change to the network protocol, and you will get polite error messages if you try to connect to a newer server with an older client or _vice versa_. There is still no _need_ to update the client--it'll still do local stuff like searching for files completely fine. Read my release posts and judge for yourself what you want to do.

## clean installs

**This is only relevant if you update and cannot boot at all.**

Very rarely, hydrus needs a clean install. This can be due to a special update like when we moved from 32-bit to 64-bit or needing to otherwise 'reset' a custom install situation. The problem is usually that a library file has been renamed in a new version and hydrus has trouble figuring out whether to use the older one (from a previous version) or the newer.

In any case, if you cannot boot hydrus and it either fails silently or you get a crash log or system-level error popup complaining in a technical way about not being able to load a dll/pyd/so file, you may need a clean install, which essentially means clearing any old files out and reinstalling.

However, you need to be careful not to delete your database! It sounds silly, but at least one user has made a mistake here. The process is simple, do not deviate:

*   Make a backup if you can!
*   Go to your install directory.
*   Delete all the files and folders except the 'db' dir (and all of its contents, obviously).
*   Reinstall/extract hydrus as you normally do.

After that, you'll have a 'clean' version of hydrus that only has the latest version's dlls. If hydrus still will not boot, I recommend you roll back to your last working backup and let me, hydrus dev, know what your error is.

## big updates

If you have not updated in some time--say twenty versions or more--doing it all in one jump, like v250->v290, is likely not going to work. I am doing a lot of unusual stuff with hydrus, change my code at a fast pace, and do not have a ton of testing in place. Hydrus update code often falls to [bitrot](https://en.wikipedia.org/wiki/Software_rot), and so some underlying truth I assumed for the v255->v256 code may not still apply six months later. If you try to update more than 50 versions at once (i.e. trying to perform more than a year of updates in one go), the client will give you a polite error rather than even try.

As a result, if you get a failure on trying to do a big update, try cutting the distance in half--try v270 first, and then if that works, try v270->v290. If it doesn't, try v260, and so on.

If you narrow the gap down to just one version and still get an error, please let me know. I am very interested in these sorts of problems and will be happy to help figure out a fix with you (and everyone else who might be affected).

## backing up

**Maintaining a regular backup is important for hydrus.** The program stores a lot of complicated data that you will put hours and hours of work into, and if you only have one copy and your hard drive breaks, you could lose everything. This has happened before, and it sucks to go through. Don't let it be you.

If you do not already have a backup routine for your files, this is a great time to start. I now run a backup every week of all my data so that if my computer blows up or anything else awful happens, I'll at worst have lost a few days' work. Before I did this, I once lost an entire drive with tens of thousands of files, and it felt awful. If you are new to saving a lot of media, I hope you can avoid what I felt. ;\_;

I use [ToDoList](http://abstractspoon.com/) to remind me of my jobs for the day, including backup tasks, and [FreeFileSync](http://sourceforge.net/projects/freefilesync/) to actually mirror over to an external usb drive. I recommend both highly (and for ToDoList, I recommend hiding the complicated columns, stripping it down to a simple interface). It isn't a huge expense to get a couple-TB usb drive either--it is **absolutely** worth it for the peace of mind.

By default, hydrus stores all your user data in one location, so backing up is simple:

*   #### the simple way - inside the client
    
    Go _database->set up a database backup location_ in the client. This will tell the client where you want your backup to be stored. A fresh, empty directory on a different drive is ideal.
    
    Once you have your location set up, you can thereafter hit _database->update database backup_. It will lock everything and mirror your files, showing its progress in a popup message. The first time you make this backup, it may take a little while (as it will have to fully copy your database and all its files), but after that, it will only have to copy new or altered files and should only ever take a couple of minutes.
    
    Advanced users who have migrated their database across multiple locations will not have this option--use an external program in this case.
    
*   #### the powerful way - using an external program
    
    If you would like to integrate hydrus into a broader backup scheme you already run, or you are an advanced user with a complicated hydrus install that you have migrated across multiple drives, then you need to backup two things: the client\*.db files and your client\_files directory(ies). By default, they are all stored in install\_dir/db. The .db files contain your settings and file metadata like inbox/archive and tags, while the client\_files subdirs store your actual media and its thumbnails. If everything is still under install\_dir/db, then it is usually easiest to just backup the whole install dir, keeping a functional 'portable' copy of your install that you can restore no prob. Make sure you keep the .db files together--they are not interchangeable and mostly useless on their own!
    
    Shut the client down while you run the backup, obviously.
    
!!! danger
    Do not put your live database in a folder that continuously syncs to a cloud backup. Many of these services will interfere with a running client and can cause database corruption. If you still want to use a system like this, either turn the sync off while the client is running, or use the above backup workflows to safely backup your client to a separate folder that syncs to the cloud.

I recommend you always backup before you update, just in case there is a problem with my code that breaks your database. If that happens, please [contact me](contact.html), describing the problem, and revert to the functioning older version. I'll get on any problems like that immediately.

[Let's import some files! ---->](getting_started_files.html)