# 22.2.1
- [ type: FEATURE MODIFICATION] add 'page_limit' parameter to !get_logs command (default: 15)  
- [ type: REMOVAL ] remove astrobot/colors.py
- [ type: IMPL ] implement colors into Astrobot (as Astrobot().colors)
- [ type: DEV-DEP-ADD ] *add 'radon'>=5.1.0
- [ type: DB-EDIT ] change 'user_moderation' primary_key to sequenced ID ('user_moderation_sequence')
- [ type: DB-EDIT ] remove table 'user_moderation'
    - incorporated data into new 'guild_user_obj' table as 'moderation_info' column
- [ type: DB-EDIT ] add new table 'guild_user_obj'
    - holds extra info about a guild member
    - FUTURE: plan to use this table in the future for XP and other community features
- [ type: BUG-FIX ] fixed issue where !modinfo showed incorrect counts
- [ type: BUG-FIX ] fixed issue where stale reminder timers were not properly handled on bot init

# 22.1.8d1
- [ type: FEATURE ] overhaul !time command
    - command now uses GeoNames API for timezone information
    - search by city/location instead of timezone
- [ type: PATCH ] check if user's 'communication_disabled_until' is stale before denying mute (thanks discord :p)
- [ type: DEP-ADD] *add 'geopy[timezone]'==2.2.0