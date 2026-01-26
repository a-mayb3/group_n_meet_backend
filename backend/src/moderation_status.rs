pub enum ModerationStatus{
    GoodToGo,
    UnderRevision,
    Removed
}

impl Default for ModerationStatus{
    fn default() -> Self {
        ModerationStatus::GoodToGo
    }
}