use chrono::prelude::*;
use uuid::Uuid;

enum UserType{
    Standard,
    Admin
}

impl Default for UserType{
    fn default() -> Self {
        UserType::Standard
    }
}

#[derive(Debug)]
pub struct User {
    uuid: Uuid,
    display_name: String,
    description: String,
    user_type: UserType,
    created_at: DateTime<Utc>,
    moderation_status: ModerationStatus
}

impl Default for User{
    fn default() -> Self{
        User {
            uuid: Uuid::now_v7(),
            display_name: String::default(),
            description: String::default(),
            user_type: UserType::default(),
            moderation_status: ModerationStatus::default(),
            created_at: Utc::now()
        }
    }
}

impl User{
    pub fn builder() -> UserBuilder
    {
        UserBuilder::default()
    }
    pub fn is_admin(&self) -> bool {
        matches!(self.user_type, UserType::Admin)
    }
}

/* UserBuilder */

#[derive(Default)]
pub struct UserBuilder{
    display_name: String,
    description : String,
    user_type: UserType
}
impl UserBuilder{
    pub fn build(self) -> User {
        User{
            uuid: Uuid::now_v7(),
            display_name: self.display_name,
            description: self.description,
            user_type: self.user_type,
            moderation_status: ModerationStatus::default(),
            created_at: Utc::now()
        }
    }
    pub fn display_name(mut self, display_name: String) -> UserBuilder {
        self.display_name = display_name;
        self
    }
    pub fn description(mut self, description: String) -> UserBuilder {
        self.description = description;
        self
    }
    pub fn user_type(mut self, user_type: UserType) -> UserBuilder {
        self.user_type = user_type;
        self
    }
}

