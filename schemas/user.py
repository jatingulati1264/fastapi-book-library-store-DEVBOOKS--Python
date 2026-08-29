def UserEntity(item) -> dict:
    return {
        "user_id": item["user_id"],
        "user_name":  item["user_name"],
        "user_email":  item["user_email"],
        "user_password":  item["user_password"],
        "user_type":  item["user_type"],
        "token":  item["token"],
        "user_created_at": item.get("user_created_at", "N/A"),
    }

def UsersEntity(items) -> list:
    return [
        UserEntity(item) for item in items
    ]