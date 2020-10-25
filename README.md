# twitch-clips-downloader

## Disclaimer:
This script is not official and not endorsed by twitch.tv

Using this script is probably a TOS violation (although a minor one) that could maybe result in you getting banned (this script behaves just like a human would except the shit browesers add but who knows, twitch might get angry)

## Features:
This script allows you to download all of the clips made by you, it came out of my need to save clips I've made in the recent dmca drama and removal of twitch clips and vods of streamers.

* Alongside with just downloading the clips you can limit the amount of clips you want to download, sort the clips by top viewed (and maybe only download your 20 top viewed clips). Refer to Arguements for more info about this.
* You can change the filename to have information you might find interesting in the order you want it such as views game and more. This allows you to sort your downloads by game, or top viewed clips while viewing it all on your pc. Refer to Formatting the filename for more info.
* This script also lets you continue from the same page you stopped downloading so you don't have to start all over again. Refer to cursor section in Arguements for more info

## Requirements:
python (works with 3.7.0, probably compatible with other 3.6+ versions)

requests library (install by running the following command in cmd "pip install requests")

your twitch oauth token, follow the instructions below to find it.

## Getting your OAuth token:
We have to use the same token twitch uses to authenticate us while browsing their website because afaik you can't access this part of their api with
a 3rd party developer generated oauth token. This means this token has almost if not every permission in the book, 

DO NOT SHARE YOUR OAUTH TOKEN!

The code in this script only runs on your computer and communicates with twitch.tv servers like it already does while browsing this website and that's it. So as long as you don't share this token it will not be exposed to malicious parties.

I'm aware of [this](https://dev.twitch.tv/docs/api/reference#get-clips) endpoint but this doesn't support viewing a list of clips made by the user. Afaik only twitch has access to that which is why we're using their token.

### Getting the token:
###### (This tutorial was made on chrome but it's probably really similar on Firefox)
1. First go [this link](https://dashboard.twitch.tv/content/clips) (you can probably do it in any part of twitch but who cares)
1. Right click, and choose inspect element
1. Refresh the page while having inspect element open
1. Switch to network tab
1. Under the 'Name' column look for gql and click on it
1. Under the newly opened tab click on 'Headers' and under 'Request Headers' copy the alpha numeric gibrish in the 'Authorization' row. This script expects to get this string without the word OAuth before.

The hard part is done, we'll use it the Usage section.
## Usage:
1. Place the clips_downloader.py file in the folder you want to save your clips at
1. Open cmd/powershell/terminal inside that folder. You can navigate with the cd command to that folder or hold down shift and right click inside the folder and choose 'Open Powershell window here'
1. Type python.exe clips_downloader.py --oauth \<string from Getting your OAuth token\> to start downloading all of your clips.
  While downloading, every about 20 clips a cursor string will appear, use this if you want to continue from this page next time by starting the script again and adding the arguement --cursor \<string\>
## Arguements:
  ### Required arguments:
  * --oauth or -o \<string\> this is the token linked to your account and is used to access all of your clips.
  ### Optional arguements:
  * --cursor or -cu \<string\> page value, treat this as a checkpoint. If you want to continue from roughly the same spot you stopped. every time the page changes a new string will be printed.
  * --client_id or -cid \<string\> you wouldn't want to use this most of the time because the oauth has to match the client id, default value is twitch's client id (there might be more than one value so you can edit this if the oauth you have wasn't generated with this client_id. To find twitch's client_id used with your oauth follow Getting your token and one row under Authorization (where we got our oauth from there's a client_id value). You should use this one if the default one built in the script fails you.
  * --limit or -li \<int\> limit of how many clips you want to download, if not specified all clips will be downloaded.
  * --fname or -fn \<string\> \<string\> \<string\>... combination of values, this is used to format the file name on your PC. The default format for a file name is: views- \<number\>_name- \<clip_name\>.mp4. Please refer to here if you want to learn how to customize it.
  * --append_char or -ac \<string\> character or string (preferebly a small one) seperating the fname values mentioned above. Please refer to here if you want to learn more.
  * --views or -v this does not require a value afterwards. if used, the clips will be sorted by top viewed.
## Formatting the filename
### --fname arguement
You might've seen the --fname arguement and wondered what it does.

This arguement allows you to change the formatting of the file name, for example while the default file name will be views- 1_name- clipname.mp4 you can use more variables from the original twitch clip such as time and date, url, slug (the end of the url), user that clipped, streamer, game, views and title to customize your filename.
Currently the output is not fully customizable, you can choose the order these variables will appear but before each of them is added a word describing them.

For example choosing to have the title followed by views and streamer will generate the following file name: title- PogChamp no way this just happened_views- 15_streamer-m0xyy
Currently the words preceding these values are not changeable (unless you change the append_word dictionary- if you do that make sure windows likes all the characters, it doesn't like +/: and more in file names)

I hope you get the idea now I'll teach you how to use it.

The following list shows the pointer and value it points to:

###### remove ' from values
* '%t' - refrencing to clip title
* '%d' - refrencing to the time and date that clip was taken
* '%v' - refrencing to the amount of views this clip has
* '%l' - refrencing to the user (login) that clipped this
* '%g' - refrencing to the game the streamer was in this clip
* '%s' - refrencing to the streamer this clip was clipped from
* '%li' - refrencing the link to the clip, in the actual filename this link will be missing characters like : and / because windows does not allow these as file names
* '%sl' - refrencing the slug, which is the unique part of the clip link. for example, in this clip https://clips.twitch.tv/PlainAlluringKimchiMoreCowbell the slug is PlainAlluringKimchiMoreCowbell

Here's an example of formatting the filename as mentioned before in the order of- title followed by views and streamer:

python.exe clips_downloader.py --oauth xxxxxxxxxx --fname %t %v %s

The result will be: title- PogChamp no way this just happened_views- 15_streamer-m0xyy

### --append_char argument
You might've noticed from the result above that between each variable there's an underscore seperating them. That's because underscore is the default append_char

This could be changed by using the --append_char arguement. You don't want to have a lot of characters as your seperator as they might repeat a lot in the file name (and windows limits you to 260 chars for path + file name)

Here's an example of using a custom append character:

python.exe clips_downloader.py --oauth xxxxxxxxxx --append_char _0\_0

The result will use the default fname because we didn't supply a replacement: views- 1_0\_0name- clipname.mp4
If we want to use space(s) as appened_char we could do it by using single quotetion marks like this: --append_char ' - ' the result will be this: views- 1 - name- clipname.mp4

## Ending
I might add streamer functionality to this script to download their top clips in the future if there's demand. Other than that, I will fix bugs and add some small features in the future. Hope this script will be of use to you.
