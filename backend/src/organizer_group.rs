use uuid::Uuid;
use chrono::prelude::*;

pub struct OrganizerGroup{
    uuid: Uuid,
    name: String,
    description: String,
    created_at: DateTime<Utc>
}
