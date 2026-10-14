import csv
import json

import numpy as np
import pandas as pd

# Подготовка

customers_str = '''customer_id,name,city,registration_date,segment
c1,Анна Иванова,Москва,2025-11-02,розница
c2,Петр Сидоров,Санкт-Петербург,2025-12-15,розница
c3,Мария Петрова,Москва,2026-01-05,опт
c4,Иван Кузнецов,Казань,2025-10-20,розница
c5,Ольга Смирнова,Москва,2026-01-10,опт
c6,Дмитрий Волков,Новосибирск,2025-09-30,розница
c7,Елена Морозова,Санкт-Петербург,2026-01-12,опт
c8,Сергей Попов,Казань,2025-12-01,розница'''

products_str = '''product_id,name,category,unit_price,in_stock
p1,Python для начинающих,Книги,650,yes
p2,Наушники,Электроника,2300,yes
p3,Чистый код,Книги,900,yes
p4,Мышь,Электроника,550,yes
p5,Алгоритмы,Книги,1200,no
p6,Футболка,Одежда,800,yes
p7,Джинсы,Одежда,2500,yes
p8,Клавиатура,Электроника,1500,yes
p9,Куртка,Одежда,4500,yes
p10,Грокаем алгоритмы,Книги,1100,yes'''

orders_str = '''order_id,order_date,customer_id,product_id,quantity,status
1,2026-01-10,c1,p1,2,completed
2,2026-01-10,c2,p2,1,completed
3,2026-01-11,c3,p3,5,completed
4,2026-01-11,c1,p4,3,completed
5,2026-01-12,c4,p6,2,completed
6,2026-01-12,c2,p8,1,cancelled
7,2026-01-13,c5,p9,1,completed
8,2026-01-13,c3,p7,4,completed
9,2026-01-14,c6,p2,2,completed
10,2026-01-14,c1,p3,1,completed
11,2026-01-15,c7,p10,10,completed
12,2026-01-15,c4,p4,x,completed
13,2026-01-16,c8,p6,3,pending
14,2026-01-16,c5,p8,2,completed
15,2026-01-17,c2,p1,,completed
16,2026-01-17,c3,p9,2,completed
17,2026-01-18,c6,p99,1,completed
18,2026-01-18,c1,p2,1,completed
19,2026-01-19,c99,p3,2,completed
20,2026-01-19,c7,p7,3,completed
21,2026-01-20,c4,p8,-1,completed
22,2026-01-20,c8,p4,4,cancelled
23,2026-01-21,c5,p10,6,completed
24,2026-01-21,c3,p2,2,completed
25,2026-01-22,c1,p6,1,completed
26,2026-01-22,c2,p3,3,completed
27,2026-01-23,c6,p9,1,completed
28,2026-01-23,c7,p8,2,completed'''

def get_rows(data_str):
    return list(csv.reader(data_str.splitlines()))

customers_rows = get_rows(customers_str)
products_rows = get_rows(products_str)
orders_rows = get_rows(orders_str)

# ЭТАП 1

def save_dataset(rows, filename):
   with open(filename, 'w', newline='', encoding='utf-8') as file:
    csv.writer(file).writerows(rows)

# save_dataset(customers_rows, 'customers.csv')
# save_dataset(products_rows, 'products.csv')
# save_dataset(orders_rows, 'orders.csv')

# ЭТАП 2

def load_file_dict(filename, key):
  result = {}

  try:
    with open(filename, 'r', encoding='utf-8') as file:
      for row in csv.DictReader(file):
        result[row[key]] = row
  except FileNotFoundError:
    print(f"Ошибка: Файл {filename} не найден!")

  return result

def load_products(filename):
  products = load_file_dict(filename, 'product_id')

  for value in products.values():
    value['unit_price'] = float(value['unit_price'])

  return products

def load_customers(filename):
  return load_file_dict(filename, 'customer_id')

# products_dict = load_products('products.csv')
# customers_dict = load_customers('customers.csv')

# ЭТАП 3

def validate_orders(filename, products, customers, log_file='rejected.csv'):
  valid = []
  rejected = []

  with open(filename, 'r', encoding='utf-8') as file:
    for row in csv.DictReader(file):
      try:
        format_quantity = int(row['quantity'])
      except ValueError:
        rejected.append((row['order_id'], 'нечисловое количество'))
        continue

      if format_quantity <= 0:
        rejected.append((row['order_id'], 'неположительное количество'))
      elif row['product_id'] not in products:
        rejected.append((row['order_id'], 'неизвестный товар'))
      elif row['customer_id'] not in customers:
        rejected.append((row['order_id'], 'неизвестный покупатель'))
      else:
        valid.append({ **row, 'quantity': format_quantity })

  with open(log_file, 'w', newline='', encoding='utf-8') as file:
    csv.writer(file).writerows([('order_id', 'reject_reason'), *rejected])

  return valid, rejected

# valid, rejected = validate_orders("orders.csv", products_dict, customers_dict)

# Этап 4

def enrich_orders(valid_orders, products, customers):
  enriched = []

  for order in valid_orders:
    product = products[order['product_id']]
    customer = customers[order['customer_id']]
    enriched.append({
      **order,
      'product': product['name'],
      'category': product['category'],
      'price': product['unit_price'],
      'customer': customer['name'],
      'city': customer['city'],
      'segment': customer['segment'],
      'revenue': order['quantity'] * product['unit_price']
    })

  return enriched

# enriched = enrich_orders(valid, products_dict, customers_dict)

# Этап 5

def normalize_str(value):
  return value.strip().title()

def normalize_orders(orders):
  normalized = []

  for order in orders:
    normalized.append({
      **order,
      'customer': normalize_str(order['customer']),
      'city': normalize_str(order['city']),
      'category': normalize_str(order['category'])
    })

  return normalized

# normalize_enriched = normalize_orders(enriched)

# Этап 6

def completed_only(orders):
  completed = []

  for order in orders:
    if order['status'] == 'completed':
      completed.append(order)

  return completed

def total_revenue(orders):
  total = 0

  for order in orders:
    total += order['revenue']

  return total

# completed = completed_only(normalize_enriched)

def revenue_by(orders, field):
  total_by_types = {}

  for order in orders:
    group_key = order[field]
    total_by_types[group_key] = total_by_types.get(group_key, 0) + order['revenue']

  return total_by_types

def top_customers(orders, n):
  totals = {}

  for order in orders:
    customer_name = order['customer']
    totals[customer_name] = totals.get(customer_name, 0) + order['revenue']

  return sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:n]

def top_products(orders, n):
  totals = {}

  for order in orders:
    product_name = order['product']
    totals[product_name] = totals.get(product_name, 0) + order['quantity']

  return sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:n]


# Этап 7

def revenue_analytics(orders):
  result = { 'mean': 0.0, 'median': 0.0, 'std': 0.0 , 'q25': 0.0, 'q50': 0.0, 'q75': 0.0 }
  revenue_list = np.array([o['revenue'] for o in orders])

  result['mean'] = np.mean(revenue_list)
  result['median'] = np.median(revenue_list)
  result['std'] = np.std(revenue_list)
  result['q25'] = np.percentile(revenue_list, 25)
  result['q50'] = np.percentile(revenue_list, 50)
  result['q75'] = np.percentile(revenue_list, 75)

  return result

# analytics_result = revenue_analytics(completed)

def find_anomalies(orders):
  orders_array = np.array(orders, dtype=object)
  revenue = np.array([o['revenue'] for o in orders_array], dtype=float)
  threshold = np.mean(revenue) + np.std(revenue) * 2
  mask = revenue > threshold

  return orders_array[mask]

# Этап 8

def build_dataframe(orders):
  return pd.DataFrame(orders)

def category_segment_pivot(df):
  return df.pivot_table(
    index="category",
    columns="segment",
    values="revenue",
    aggfunc="sum",
    fill_value=0
  )

# df = build_dataframe(completed)
# pivot = category_segment_pivot(df)

# print(round(df["revenue"].mean(), 2))
# print(pivot)
# print(df.groupby('category')['revenue'].sum())

# Этап 9

def top_report(list_pairs):
    report_lines = []

    for [word, count] in list_pairs:
      report_lines.append(f"  {word} — {count:.2f}")

    return "\n".join(report_lines)

def run_pipeline():
  save_dataset(customers_rows, 'customers.csv')
  save_dataset(products_rows, 'products.csv')
  save_dataset(orders_rows, 'orders.csv')

  products_dict = load_products('products.csv')
  customers_dict = load_customers('customers.csv')
  valid, rejected = validate_orders("orders.csv", products_dict, customers_dict)
  enriched = enrich_orders(valid, products_dict, customers_dict)
  normalize_enriched = normalize_orders(enriched)
  completed = completed_only(normalize_enriched)
  analytics_result = revenue_analytics(completed)
  anomalies = find_anomalies(completed)
  total = total_revenue(completed)
  category_revenue = revenue_by(completed, "category")
  segment_revenue = revenue_by(completed, "segment")
  city_revenue = revenue_by(completed, "city")
  top_clients = top_customers(completed, 3)

  return {'valid': valid, 'rejected': rejected, 'completed': completed, 'analytics_result': analytics_result, 'anomalies': anomalies, 'total': total, 'category_revenue': category_revenue, 'segment_revenue': segment_revenue, 'city_revenue': city_revenue, 'top_clients': top_clients}

def get_full_report(data):
  valid = data['valid']
  rejected = data['rejected']
  completed = data['completed']
  analytics_result = data['analytics_result']
  anomalies = data['anomalies']
  total = data['total']
  category_revenue = data['category_revenue']
  segment_revenue = data['segment_revenue']
  top_clients = data['top_clients']

  return f'''ОТЧЕТ АНАЛИТИЧЕСКОЙ ПЛАТФОРМЫ
Обработано строк заказов: {len(valid) + len(rejected)}
Отбраковано некорректных: {len(rejected)}
Корректных заказов: {len(valid)}
Завершенных заказов: {len(completed)}

Общая выручка: {total:.2f}
Средний чек: {analytics_result['mean']:.2f}
Медианный чек: {analytics_result['median']:.2f}

Выручка по категориям:
{top_report(category_revenue.items())}

Выручка по сегментам:
{top_report(segment_revenue.items())}

Топ покупателей:
{top_report(top_clients)}

Аномальных заказов: {len(anomalies)}'''

def export_json(filename, data):
  valid = data['valid']
  rejected = data['rejected']
  completed = data['completed']
  analytics_result = data['analytics_result']
  anomalies = data['anomalies']
  total = data['total']
  category_revenue = data['category_revenue']
  segment_revenue = data['segment_revenue']
  top_clients = data['top_clients']

  with open(filename, 'w', encoding='utf-8') as file:
    json.dump({
        "total_rows": len(valid) + len(rejected),
        "rejected": len(rejected),
        "valid": len(valid),
        "completed": len(completed),
        "total_revenue": round(total, 2),
        "average_check": round(analytics_result['mean'], 2),
        "median_check": round(analytics_result['median'], 2),
        "revenue_by_category": category_revenue,
        "revenue_by_segment": segment_revenue,
        "top_customers": top_clients,
        "anomalies": len(anomalies)
    }, file, ensure_ascii=False, indent=2)

def export_csv(rows, filename, key = 'category'):
  rows_with_title = {key: 'revenue', **revenue_by(rows, key)}

  with open(filename, 'w', newline='', encoding='utf-8') as file:
    csv.writer(file).writerows(rows_with_title.items())

# print(get_full_report(analytics_full_data))
# export_json('full_report.json', analytics_full_data)
# export_csv(analytics_full_data['completed'], 'report.csv')

# Этап 10

def revenue_sub_menu(data):
  category_revenue = data['category_revenue']
  segment_revenue = data['segment_revenue']
  city_revenue = data['city_revenue']

  while True:
    try:
      section = input('введите название раздела — категория, город или сегмент: ').strip().lower()
    except EOFError:
      section = 'категория'

    if section == 'сегмент':
      return f'''Выручка по сегментам:
{top_report(segment_revenue.items())}'''
    elif section == 'город':
      return f'''Выручка по городам:
{top_report(city_revenue.items())}'''
    elif section == 'категория':
      return f'''Выручка по категориям:
{top_report(category_revenue.items())}'''
    else:
      print("Пожалуйста, введите только название раздела — категория, город или сегмент" + "\n")

def get_anomalies_report(anomalies):
  if len(anomalies) == 0:
    return 'Аномальных заказов нет'

  lines = [
    f"  заказ {o['order_id']} — {o['customer']}, {o['product']}: {o['revenue']:.2f}"
    for o in anomalies
  ]

  return f'Аномальные заказы – {len(lines)}:\n' + '\n'.join(lines)

def console():
  input_text = """1 — Полный отчет
2 — Выручка по выбранному разделу
3 — Топ покупателей
4 — Аномальные заказы
5 — Сохранить отчеты в файлы
0 — Выход
Выберите действие: """

  analytics_full_data = run_pipeline()

  while True:
    try:
      code = input(input_text).strip()
    except EOFError:
      code = '0'

    if code == '0':
      print("До свидания!")
      break
    elif code == '1':
      print(get_full_report(analytics_full_data))
    elif code == '2':
      print(revenue_sub_menu(analytics_full_data))
    elif code == '3':
      print(f'''Топ покупателей:\n{top_report(analytics_full_data['top_clients'])}''')
    elif code == '4':
      print(get_anomalies_report(analytics_full_data['anomalies']))
    elif code == '5':
      export_json('full_report.json', analytics_full_data)
      export_csv(analytics_full_data['completed'], 'category_revenue.csv')
      export_csv(analytics_full_data['completed'], 'segment_revenue.csv', 'segment')
      export_csv(analytics_full_data['completed'], 'city_revenue.csv', 'city')
    else:
      print("Пожалуйста, введите число от 0 до 5" + "\n")

console()

# ТЕСТЫ
def run_checks():
  data = run_pipeline()
  valid = data['valid']
  rejected = data['rejected']
  completed = data['completed']

  assert len(valid) == 23
  assert rejected == [
      ("12", "нечисловое количество"),
      ("15", "нечисловое количество"),
      ("17", "неизвестный товар"),
      ("19", "неизвестный покупатель"),
      ("21", "неположительное количество"),
  ]
  assert completed[1]["revenue"] == 2300.0
  assert completed[1]["quantity"] == 1

  assert len(completed) == 20
  assert total_revenue(completed) == 86350.0
  assert revenue_by(completed, "category") == {
      "Одежда": 37900.0, "Книги": 27000.0, "Электроника": 21450.0}
  assert revenue_by(completed, "segment") == {"опт": 63700.0, "розница": 22650.0}
  assert top_customers(completed, 3) == [
      ("Мария Петрова", 28100.0), ("Елена Морозова", 21500.0),
      ("Ольга Смирнова", 14100.0)]
  assert top_products(completed, 3) == [
      ("Грокаем алгоритмы", 16), ("Чистый код", 9), ("Джинсы", 7)]

  assert len(find_anomalies(completed)) == 1

  df = build_dataframe(completed)
  assert round(df["revenue"].mean(), 2) == 4317.5

  pivot = category_segment_pivot(df)
  assert pivot.loc["Книги", "опт"] == 22100.0
  assert pivot.loc["Электроника", "розница"] == 10850.0
  assert pivot.values.sum() == 86350.0

  for field in ("category", "segment", "city"):
    manual = revenue_by(completed, field)
    pandas_result = df.groupby(field)["revenue"].sum().to_dict()

    assert manual.keys() == pandas_result.keys(), f"{field}: разные ключи"
    for key, value in manual.items():
      assert abs(value - pandas_result[key]) < 0.01, f"{field}/{key}: {value} != {pandas_result[key]}"

  assert abs(total_revenue(completed) - df["revenue"].sum()) < 0.01
  assert abs(revenue_analytics(completed)["mean"] - df["revenue"].mean()) < 0.01
  assert abs(revenue_analytics(completed)["median"] - df["revenue"].median()) < 0.01

  pandas_top = df.groupby("customer")["revenue"].sum().sort_values(ascending=False).head(3)
  assert [name for name, _ in top_customers(completed, 3)] == pandas_top.index.tolist()

  pandas_top_products = df.groupby("product")["quantity"].sum().sort_values(ascending=False).head(3)
  assert top_products(completed, 3) == list(pandas_top_products.items())

  print("Все проверки пройдены")

# run_checks()
