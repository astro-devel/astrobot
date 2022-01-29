# 21.1.8d1
- [ type: FEATURE ] overhaul !time command
    - command now uses GeoNames API for timezone information
    - search by city/location instead of timezone
- [ type: PATCH ] check if user's 'communication_disabled_until' is stale before denying mute (thanks discord :p)
- [ type: DEP-ADD] *add 'geopy[timezone]'==2.2.0