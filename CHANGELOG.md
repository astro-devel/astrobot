# 22.2.2
- [ FEATURE_MODIFICATION ] update !remindme command response
- [ BOT_MODIFICATION ] update gateway intents only to specific intents needed, instead of all intents (saves log space)
- [ LOCKFILE_DEP_UPDATE ] updated the following lockfile dependencies:
    - pycord -> 2.0.0b3
    - scalene -> 1.5.3
    - numpy -> 1.22.2
    - httpcore -> 0.14.7

# 22.2.1
- [ FEATURE_MODIFICATION] add 'page_limit' parameter to !get_logs command (default: 15)  
- [ REMOVAL ] remove astrobot/colors.py
- [ IMPL ] implement colors into Astrobot (as Astrobot().colors)
- [ DEV_DEP_ADD ] *add 'radon'>=5.1.0
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
- [ DEP_ADD] *add 'geopy[timezone]'==2.2.0