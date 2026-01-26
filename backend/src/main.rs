use actix_web::{App, HttpServer, web};
use sqlx::postgres::PgPoolOptions;
use std::env;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv::dotenv().ok();
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));

    let database_user: String =
        env::var("POSTGRES_USER").unwrap_or_else(|_| "postgres".to_string());
    let database_password: String =
        env::var("POSTGRES_PASSWORD").unwrap_or_else(|_| "password".to_string());
    let database_url: String = format!(
        "postgres://{}:{}@localhost/group_n_meet",
        database_user, database_password
    );

    let server_port = env::var("SERVER_PORT").unwrap_or_else(|_| "8080".to_string());
    let server_address = format!("127.0.0.1:{}", server_port);

    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await
        .expect("Failed to create pool");

    // Create the database if it doesn't exist
    sqlx::query(format!("CREATE DATABASE IF NOT EXISTS group_n_meet OWNER {};", database_user).as_str())
        .execute(&pool)
        .await
        .unwrap();

    log::info!("Starting server on {}", server_address);
    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(pool.clone()))
            .route("/health", web::get().to(health_check))
    })
    .bind(&server_address)?
    .run()
    .await
}

async fn health_check() -> &'static str {
    "OK"
}
