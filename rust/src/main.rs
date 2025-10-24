use axum::{
    extract::Extension,
    routing::get,
    Json, Router,
};
use clap::Parser;
use dotenvy::dotenv;
use serde::Serialize;
use sqlx::{postgres::PgPoolOptions, Pool, Postgres};
use std::{net::SocketAddr, sync::Arc, time::Instant};
use tower_http::trace::TraceLayer;
use tracing::{info, Level};

#[derive(Parser, Debug)]
#[command(author, version, about)]
struct Args {
    /// Number of workers (Tokio worker threads)
    #[arg(short, long, default_value_t = 1)]
    workers: usize,

    /// Port to run the server on
    #[arg(short, long, default_value_t = 8001)]
    port: u16,
}

#[derive(Serialize)]
struct Data {
    field1: String,
    field2: i32,
}

type AppState = Arc<Pool<Postgres>>;

async fn test1(Extension(pool): Extension<AppState>) -> Json<Vec<Data>> {
    let start = Instant::now();

    let rows = sqlx::query!(
        r#"
        SELECT field1, field2 
        FROM data 
        WHERE field2 > 995
        "#
    )
    .fetch_all(&*pool)
    .await
    .unwrap_or_else(|e| {
        tracing::error!("Database error: {}", e);
        vec![]
    });

    let result = rows
        .into_iter()
        .map(|row| Data {
            field1: row.field1,
            field2: row.field2,
        })
        .collect::<Vec<_>>();

    info!("Query took: {:.2?}", start.elapsed());
    Json(result)
}

#[tokio::main]
async fn main() {
    // Загружаем .env
    dotenv().ok();

    // Инициализация логирования
    tracing_subscriber::fmt()
        .with_max_level(Level::INFO)
        .init();

    // Парсим аргументы
    let args = Args::parse();

    // Формируем URL подключения к БД
    let db_url = format!(
        "postgres://{}:{}@{}:{}/{}",
        std::env::var("DB_USER").expect("DB_USER must be set"),
        std::env::var("DB_PASSWORD").expect("DB_PASSWORD must be set"),
        std::env::var("DB_IP").unwrap_or_else(|_| "localhost".to_string()),
        std::env::var("DB_PORT").unwrap_or_else(|_| "5432".to_string()),
        std::env::var("DB_NAME").expect("DB_NAME must be set"),
    );

    // Создаём пул соединений
    let pool = PgPoolOptions::new()
        .max_connections(50)
        .connect(&db_url)
        .await
        .expect("Failed to create Postgres connection pool");

    let shared_state = Arc::new(pool);

    // Создаём роутер
    let app = Router::new()
        .route("/api/test1", get(test1))
        .layer(Extension(shared_state))
        .layer(TraceLayer::new_for_http());

    let addr = SocketAddr::from(([0, 0, 0, 0], args.port));
    info!("Server running on http://{}", addr);

    // Запускаем сервер с нужным числом воркеров
    let listener = tokio::net::TcpListener::bind(&addr)
        .await
        .expect("Failed to bind address");

    info!("OpenAPI docs: not included (add utoipa if needed)");

    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await
        .expect("Server error");
}

async fn shutdown_signal() {
    tokio::signal::ctrl_c()
        .await
        .expect("Failed to install CTRL+C handler");
    info!("Shutting down...");
}