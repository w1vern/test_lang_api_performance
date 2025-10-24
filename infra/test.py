
import argparse
import asyncio
import time
from typing import List
import httpx
import numpy as np


async def fetch_url(client: httpx.AsyncClient, url: str, semaphore: asyncio.Semaphore) -> float:
    """Выполняет один запрос и возвращает время в секундах или -1 при ошибке."""
    start_time = time.perf_counter()
    try:
        async with semaphore:
            response = await client.get(url, timeout=5.0)
            response.raise_for_status()
        elapsed = time.perf_counter() - start_time
        return elapsed
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        print(f"Ошибка при запросе {url}: {e}")
        return -elapsed  # отрицательное значение для ошибок


async def benchmark_url(
    url: str,
    n_requests: int = 100,
    max_concurrent: int = 10,
    timeout: float = 30.0
) -> None:
    """
    Асинхронно отправляет n_requests запросов к url с max_concurrent одновременными соединениями.
    Выводит метрики производительности.
    """
    if n_requests <= 0 or max_concurrent <= 0:
        raise ValueError("n_requests и max_concurrent должны быть положительными")

    semaphore = asyncio.Semaphore(max_concurrent)
    limits = httpx.Limits(max_keepalive_connections=max_concurrent, max_connections=max_concurrent * 2)

    start_total = time.perf_counter()

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        tasks = [
            fetch_url(client, url, semaphore)
            for _ in range(n_requests)
        ]
        results = await asyncio.gather(*tasks)

    total_time = time.perf_counter() - start_total

    # Разделяем успешные и ошибочные результаты
    success_times: List[float] = [t for t in results if t > 0]
    error_times: List[float] = [-t for t in results if t < 0]  # положительное время даже при ошибке
    errors_count = len(results) - len(success_times)
    success_count = len(success_times)

    if success_count == 0:
        print("Все запросы завершились с ошибкой.")
        return

    # Метрики
    times_array = np.array(success_times)
    mean_time = np.mean(times_array)
    median_time = np.median(times_array)
    p90 = np.percentile(times_array, 90)
    p95 = np.percentile(times_array, 95)
    p99 = np.percentile(times_array, 99)
    min_time = np.min(times_array)
    max_time = np.max(times_array)

    # Общие метрики
    rps = success_count / total_time

    print("\n" + "="*50)
    print("РЕЗУЛЬТАТЫ БЕНЧМАРКА")
    print("="*50)
    print(f"URL: {url}")
    print(f"Всего запросов: {n_requests}")
    print(f"Макс. одновременных соединений: {max_concurrent}")
    print(f"Общее время выполнения: {total_time:.2f} сек")
    print(f"Успешных запросов: {success_count}")
    print(f"Ошибок: {errors_count}")
    print(f"Запросов в секунду (RPS): {rps:.2f}")
    print("\nВремя ответа (успешные, сек):")
    print(f"  Среднее:  {mean_time:.4f}")
    print(f"  Медиана:  {median_time:.4f}")
    print(f"  90-й:     {p90:.4f}")
    print(f"  95-й:     {p95:.4f}")
    print(f"  99-й:     {p99:.4f}")
    print(f"  Мин:      {min_time:.4f}")
    print(f"  Макс:      {max_time:.4f}")
    print("="*50)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple load tester using httpx")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("-n", type=int, default=100, help="Total number of requests")
    parser.add_argument("-c", "--concurrency", type=int, default=10, help="Concurrency")
    #parser.add_argument("--method", default="GET", help="HTTP method")
    #parser.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout seconds")
    #parser.add_argument("--http2", action="store_true", help="Enable HTTP/2")
    args = parser.parse_args()

    asyncio.run(
        benchmark_url(
            max_concurrent=args.concurrency,
            n_requests=args.n,
            url=args.url,
        )
    )

if __name__ == "__main__":
    main()