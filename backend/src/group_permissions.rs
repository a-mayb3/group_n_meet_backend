use crate::user::User;
use crate::organizer_group::OrganizerGroup;

use uuid::Uuid;

pub struct GroupPermissions{
    user: User,
    organizer_group: OrganizerGroup,
    is_group_admin: bool
}

impl GroupPermissions{
    pub fn new(user:User, organizer_group: OrganizerGroup, is_admin:bool) -> Self{
        GroupPermissions{
            user:user,
            organizer_group:organizer_group,
            is_group_admin: is_admin
        }
    }
}
