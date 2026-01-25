use uuid::Uuid;
use chrono::prelude::*;
use sha2::{Sha256, Digest};

#[derive(Debug)]
pub struct Rsvp{
    user_uuid: Uuid,
    event_uuid : Uuid,
    hash : Vec<u8>,
    reserved_at: DateTime<Utc>,
    is_cancelled: bool
}

impl Rsvp{
    pub fn builder() -> RsvpBuilder {
        RsvpBuilder::default()
    }

    pub fn new(user_uuid: Uuid, event_uuid: Uuid) -> Self {

        let mut hasher = Sha256::new();

        hasher.update(user_uuid.as_bytes());
        hasher.update(event_uuid.as_bytes());

        let calc_hash = hasher.finalize();

        Rsvp{
            user_uuid: user_uuid,
            event_uuid: event_uuid,
            hash: calc_hash.to_vec(),
            reserved_at: Utc::now(),
            is_cancelled: false
        }
    }

}

#[derive(Default)]
pub struct RsvpBuilder{
    user_uuid: Uuid,
    event_uuid: Uuid,
    is_cancelled: bool
}
impl RsvpBuilder{
    pub fn user_uuid(mut self, user_uuid: Uuid) -> Self{
        self.user_uuid = user_uuid;
        self
    }

    pub fn event_uuid(mut self, event_uuid : Uuid) -> Self {
        self.event_uuid = event_uuid;
        self
    }

    pub fn is_cancelled(mut self, is_cancelled: bool)-> Self{
        self.is_cancelled = is_cancelled;
        self
    }

    pub fn build(self) -> Rsvp{

        let mut hasher = Sha256::new();

        hasher.update(self.user_uuid.as_bytes());
        hasher.update(self.event_uuid.as_bytes());

        let calc_hash = hasher.finalize(); //digested combined uuids

        Rsvp{
            user_uuid: self.user_uuid,
            event_uuid: self.event_uuid,
            hash: calc_hash.to_vec(),
            is_cancelled: self.is_cancelled,
            reserved_at: Utc::now()
        }
    }
}

