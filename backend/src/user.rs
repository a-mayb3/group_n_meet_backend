use chrono::prelude::*;
use uuid::Uuid;

#[derive(Debug)]
pub struct User {
    uuid: Uuid,
    display_name: String,
    description: String,
    created_at: DateTime<Utc>
}

impl Default for User{
    fn default() -> Self{
        User {
            uuid: Uuid::now_v7(),
            display_name: String::default(),
            description: String::default(),
            created_at: Utc::now()
        }
    }
}

impl User{
    pub fn builder() -> UserBuilder
    {
        UserBuilder::default()
    }
}

/* UserBuilder */

#[derive(Default)]
pub struct UserBuilder{
    display_name: String,
    description : String,
}
impl UserBuilder{
    pub fn build(self) -> User {
        User{
            uuid: Uuid::now_v7(),
            display_name: self.display_name,
            description: self.description,
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
}

