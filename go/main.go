package main

import (
  "fmt"
  "log"
  "os"
  "time"
  "runtime"

  "github.com/gofiber/fiber/v2"
  "gorm.io/driver/postgres"
  "gorm.io/gorm"

  "github.com/joho/godotenv"
)

// Data соответствует модели в Python
type Data struct {
  Field1 string `json:"field1"`
  Field2 int    `json:"field2"`
}

var db *gorm.DB

// Функция для подключения к БД
func initDB() {
	if err := godotenv.Load(".env"); err != nil {
    	log.Println("⚠️  Warning: .env file not found, using system env")
  	}	

  host := os.Getenv("DB_IP")
  port := os.Getenv("DB_PORT")
  user := os.Getenv("DB_USER")
  password := os.Getenv("DB_PASSWORD")
  name := os.Getenv("DB_NAME")
  sslmode := os.Getenv("DB_SSLMODE")

  if sslmode == "" {
    sslmode = "disable"
  }

  dsn := fmt.Sprintf(
    "host=%s user=%s password=%s dbname=%s port=%s sslmode=%s",
    host, user, password, name, port, sslmode,
  )

  var err error
  db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
  if err != nil {
    log.Fatal("failed to connect database:", err)
  }

  log.Println("Database connected successfully")
}

// Обработчик для /api/test1
func getTestData(c *fiber.Ctx) error {
  start := time.Now()

  var results []Data
  if err := db.Raw("SELECT field1, field2 FROM data WHERE field2 > ?", 995).Scan(&results).Error; err != nil {
    return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
      "error": err.Error(),
    })
  }

  fmt.Println("Query duration:", time.Since(start))
  return c.JSON(results)
}

func main() {
  runtime.GOMAXPROCS(1)
  initDB()

  app := fiber.New(fiber.Config{
    AppName: "Fiber API Example",
  })

  app.Get("/api/test1", getTestData)

  log.Fatal(app.Listen(":8004"))
}
