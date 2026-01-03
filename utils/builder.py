import discord

def parse_color(hex_color):
    if not hex_color:
        return discord.Color.default()
    try:
        return discord.Color(int(hex_color.lstrip('#'), 16))
    except ValueError:
        return discord.Color.default()

def get_permissions(perm_list):
    permissions = discord.Permissions.none()
    for perm in perm_list:
        if hasattr(permissions, perm):
            setattr(permissions, perm, True)
    return permissions

def get_overwrites(guild, roles_map, perm_data_list):
    overwrites = {}
    for perm_data in perm_data_list:
        role_name = perm_data.get('role')
        role = roles_map.get(role_name) or discord.utils.get(guild.roles, name=role_name)
        if not role:
            # Try to find @everyone if specified
            if role_name == "@everyone" or role_name == "everyone":
                role = guild.default_role
            else:
                continue
        
        overwrite = discord.PermissionOverwrite()
        for allow in perm_data.get('allow', []):
            if hasattr(overwrite, allow):
                setattr(overwrite, allow, True)
        for deny in perm_data.get('deny', []):
            if hasattr(overwrite, deny):
                setattr(overwrite, deny, False)
        
        overwrites[role] = overwrite
    return overwrites

async def build_server(guild: discord.Guild, blueprint: dict, progress_callback=None):
    # Calculate total operations for progress bar
    # 1 (deletion) + roles + categories + channels
    total_ops = 1 + len(blueprint.get('roles', [])) + len(blueprint.get('categories', [])) + sum(len(c.get('channels', [])) for c in blueprint.get('categories', []))
    current_op = 0

    async def update_progress(status):
        nonlocal current_op
        current_op += 1
        if progress_callback:
            await progress_callback(current_op, total_ops, status)

    # Intelligent Deletion
    if blueprint.get('delete_unused', False):
        await update_progress("Cleaning up old channels...")
        # Gather all names from blueprint to know what to keep
        blueprint_category_names = [c['name'] for c in blueprint.get('categories', [])]
        blueprint_channel_names = []
        for c in blueprint.get('categories', []):
            for ch in c.get('channels', []):
                blueprint_channel_names.append(ch['name'])
        
        # Delete channels not in blueprint
        for channel in guild.channels:
            # Skip the channel where the command might have been run (if possible to detect, otherwise user beware)
            # For now, we just delete if it doesn't match.
            # Safety: Don't delete if it matches a name in the blueprint (fuzzy match could be better but exact for now)
            
            if isinstance(channel, discord.CategoryChannel):
                if channel.name not in blueprint_category_names:
                    try:
                        await channel.delete()
                    except: pass
            else:
                if channel.name not in blueprint_channel_names:
                    try:
                        await channel.delete()
                    except: pass

    # Create Roles
    roles_map = {}
    # Sort roles to ensure hierarchy (bot can't manage roles above it, but we can try to create them in order)
    # We'll create them. Discord adds them at the bottom by default.
    for role_data in blueprint.get('roles', []):
        await update_progress(f"Creating role: {role_data['name']}")
        try:
            existing_role = discord.utils.get(guild.roles, name=role_data['name'])
            permissions = get_permissions(role_data.get('permissions', []))
            color = parse_color(role_data.get('color'))

            if existing_role:
                # Update existing role
                try:
                    await existing_role.edit(
                        color=color,
                        permissions=permissions,
                        hoist=role_data.get('hoist', False),
                        mentionable=role_data.get('mentionable', False)
                    )
                    roles_map[role_data['name']] = existing_role
                except Exception as e:
                    print(f"Failed to edit role {role_data['name']}: {e}")
                    roles_map[role_data['name']] = existing_role # Keep it anyway
            else:
                # Create new role
                role = await guild.create_role(
                    name=role_data['name'],
                    color=color,
                    permissions=permissions,
                    hoist=role_data.get('hoist', False),
                    mentionable=role_data.get('mentionable', False)
                )
                roles_map[role_data['name']] = role
        except Exception as e:
            print(f"Failed to create/edit role {role_data['name']}: {e}")

    # Create Categories and Channels
    for cat_data in blueprint.get('categories', []):
        await update_progress(f"Creating category: {cat_data['name']}")
        try:
            overwrites = get_overwrites(guild, roles_map, cat_data.get('permissions', []))
            
            # Check if category exists
            category = discord.utils.get(guild.categories, name=cat_data['name'])
            if not category:
                category = await guild.create_category(name=cat_data['name'], overwrites=overwrites)
            else:
                # Update overwrites if needed
                await category.edit(overwrites=overwrites)
            
            for channel_data in cat_data.get('channels', []):
                await update_progress(f"Creating channel: {channel_data['name']}")
                try:
                    channel_overwrites = get_overwrites(guild, roles_map, channel_data.get('permissions', []))
                    
                    # Check if channel exists
                    # Note: This finds the first channel with the name. 
                    # If multiple exist (which shouldn't happen with good management), it picks one.
                    existing_channel = discord.utils.get(guild.channels, name=channel_data['name'])
                    
                    if existing_channel:
                        # Update existing channel
                        await existing_channel.edit(overwrites=channel_overwrites, topic=channel_data.get('description'))
                        continue

                    if channel_data['type'] == 'text':
                        await guild.create_text_channel(
                            name=channel_data['name'], 
                            category=category, 
                            topic=channel_data.get('description'),
                            overwrites=channel_overwrites
                        )
                    elif channel_data['type'] == 'voice':
                        await guild.create_voice_channel(
                            name=channel_data['name'], 
                            category=category,
                            overwrites=channel_overwrites
                        )
                    elif channel_data['type'] == 'stage':
                        await guild.create_stage_channel(
                            name=channel_data['name'], 
                            category=category,
                            overwrites=channel_overwrites
                        )
                    elif channel_data['type'] == 'forum':
                        await guild.create_forum_channel(
                            name=channel_data['name'], 
                            category=category,
                            topic=channel_data.get('description'),
                            overwrites=channel_overwrites
                        )
                except Exception as e:
                    print(f"Failed to create channel {channel_data['name']}: {e}")
                    
        except Exception as e:
            print(f"Failed to create category {cat_data['name']}: {e}")

async def get_server_structure(guild: discord.Guild):
    """Serialize the current server structure."""
    structure = {
        "server_name": guild.name,
        "roles": [],
        "categories": []
    }

    # Serialize Roles
    for role in guild.roles:
        if role.is_default(): continue
        structure["roles"].append({
            "name": role.name,
            "color": str(role.color),
            "permissions": [p[0] for p in role.permissions if p[1]],
            "hoist": role.hoist,
            "mentionable": role.mentionable
        })

    # Serialize Categories and Channels
    for category in guild.categories:
        cat_data = {
            "name": category.name,
            "channels": []
        }
        for channel in category.channels:
            c_type = "text"
            if isinstance(channel, discord.VoiceChannel): c_type = "voice"
            elif isinstance(channel, discord.StageChannel): c_type = "stage"
            elif isinstance(channel, discord.ForumChannel): c_type = "forum"
            
            chan_data = {
                "name": channel.name,
                "type": c_type
            }
            if hasattr(channel, "topic") and channel.topic:
                chan_data["description"] = channel.topic
            
            cat_data["channels"].append(chan_data)
        structure["categories"].append(cat_data)
    
    # Handle channels without category
    no_cat_channels = [c for c in guild.channels if not c.category and not isinstance(c, discord.CategoryChannel)]
    if no_cat_channels:
        cat_data = {
            "name": "Uncategorized",
            "channels": []
        }
        for channel in no_cat_channels:
            c_type = "text"
            if isinstance(channel, discord.VoiceChannel): c_type = "voice"
            elif isinstance(channel, discord.StageChannel): c_type = "stage"
            elif isinstance(channel, discord.ForumChannel): c_type = "forum"
            
            chan_data = {
                "name": channel.name,
                "type": c_type
            }
            if hasattr(channel, "topic") and channel.topic:
                chan_data["description"] = channel.topic
            cat_data["channels"].append(chan_data)
        structure["categories"].append(cat_data)

    return structure

async def nuke_server(guild: discord.Guild):
    """Delete all channels and categories."""
    for channel in guild.channels:
        try:
            await channel.delete()
        except:
            pass
