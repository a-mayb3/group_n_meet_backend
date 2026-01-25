use uuid::Uuid;
use chrono::prelude::*;

#[derive(Debug)]
pub struct Event {
    uuid: Uuid,
    name: String,
    description: String,
    created_at: DateTime<Utc>,
    time: DateTime<Utc>,
    place: String // TODO: use an adequate type
}

impl Default for Event {
    fn default() -> Self{
        Event{
            uuid: Uuid::now_v7(),
            name: String::default(),
            description: String::default(),
            created_at: Utc::now(),
            time: DateTime::default(),
            place: String::default()
        }
    }
}

impl Event{
    pub fn builder() -> EventBuilder { EventBuilder::default() }
}

#[derive(Default, Debug)]
pub struct EventBuilder{
    name: String,
    description: String,
    time: DateTime<Utc>,
    place: String,
}
impl EventBuilder{

    pub fn name(mut self, name :String) -> Self {
        self.name = name;
        self
    }

    pub fn description (mut self, description: String) -> Self {
        self.description = description;
        self
    }

    pub fn time(mut self, time: DateTime<Utc>) -> Self{
        self.time = time;
        self
    }

    pub fn build(self) -> Event {
        Event{
            uuid : Uuid::now_v7(),
            name: self.name,
            description: self.description,
            created_at: Utc::now(),
            time: self.time,
            place: self.place
        }
    }
}
