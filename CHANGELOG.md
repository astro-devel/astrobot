# 22.2.4.patch1
- [ BUG_FIX ] fix time for '!sp nowplaying' when length is over 1 hour

# 22.2.4
- [ DEV_DEP_ADD ] black >= 22.1.0
- [ FEATURE_MODIFICATION ] added ability to add default spotify playback device
    - i.e. "!sp set device default BedroomAmp"
- [ FEATURE_MODIFICATION ] added support for podcasts and local tracks to !sp nowplaying
- [ FEATURE_MODIFICATION ] !sp nowplaying embed now displays album art dominant color

# 22.2.3.patch2
- [ BOT_MODIFICATION ] add GUILD_MEMBERS intent, in order to re-enable member caching
- [ BOT_MODIFICATION ] disable message caching
- [ ETC ] revert changes from patch 1

# 22.2.3.patch1
- [ BUG_FIX ] Guild.owner.id in !serverinfo used gateway cache function 'get_member()', which returned none
    - fixed by changing to fetch_member(), which uses REST API call
    - issue may be in other commands, will be on lookout

# 22.2.3
- [ FEATURE_MODIFICATION ] remove !slowmode_status command
    - current feature of !slowmode_status to be moved to !slowmode (as !slowmode)
        - slowmode(time) is now optional to fulfill this
        - add *reason kwarg to slowmode command, for setting audit log reason (X-Audit-Log-Reason)
            - hopefully later to be impl in !slowmodes
    - [ ADD_CMD ] !slowmodes
        - display paginated list of all active slowmodes in current guild
- [ DEP_ADD ] arrow >= 1.2.2

# 22.2.2
- [ FEATURE_MODIFICATION ] update !remindme command response
- [ BOT_MODIFICATION ] update gateway intents only to specific intents needed, instead of all intents (saves log space)

# 22.2.1
- [ FEATURE_MODIFICATION] add 'page_limit' parameter to !get_logs command (default: 15)  
- [ REMOVAL ] remove astrobot/colors.py
- [ IMPL ] implement colors into Astrobot (as Astrobot().colors)
- [ DEV_DEP_ADD ] 'radon'>=5.1.0
- [ DB_EDIT ] change 'user_moderation' primary_key to sequenced ID ('user_moderation_sequence')
- [ DB_EDIT ] remove table 'user_moderation'
    - incorporated data into new 'guild_user_obj' table as 'moderation_info' column
- [ DB_EDIT ] add new table 'guild_user_obj'
    - holds extra info about a guild member
    - FUTURE: plan to use this table in the future for XP and other community features
- [ BUG_FIX ] fixed issue where !modinfo showed incorrect counts
- [ BUG_FIX ] fixed issue where stale reminder timers were not properly handled on bot init

# 22.1.8d1
- [ FEATURE ] overhaul !time command
    - command now uses GeoNames API for timezone information
    - search by city/location instead of timezone
- [ PATCH ] check if user's 'communication_disabled_until' is stale before denying mute (thanks discord :p)
- [ DEP_ADD ] 'geopy[timezone]'==2.2.0