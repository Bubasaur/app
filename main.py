import sqlite3
from datetime import date
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.list import TwoLineAvatarIconListItem, IconRightWidget
from kivymd.uix.menu import MDDropdownMenu
from kivymd.toast import toast
from kivy.properties import StringProperty, ColorProperty, NumericProperty
from kivy.factory import Factory

# --- KV DESIGN ---
KV = '''
# 1. StatCard Design
<StatCard>:
    orientation: "vertical"
    padding: "10dp"
    size_hint: None, None
    size: "140dp", "80dp"
    radius: [12]
    elevation: 4
    md_bg_color: 0.2, 0.2, 0.2, 1
    
    MDLabel:
        text: root.title
        theme_text_color: "Secondary"
        font_style: "Caption"
        halign: "center"
    MDLabel:
        text: root.value
        theme_text_color: "Custom"
        text_color: root.color
        font_style: "H6"
        halign: "center"

# 2. GraphItem Design
<GraphItem>:
    orientation: "vertical"
    size_hint_y: None
    height: "60dp"
    padding: "5dp"
    
    MDBoxLayout:
        MDLabel:
            text: root.label_date
            theme_text_color: "Secondary"
            font_style: "Caption"
            size_hint_x: 0.3
        MDLabel:
            text: root.label_value
            theme_text_color: "Primary"
            halign: "right"
            font_style: "Caption"
            size_hint_x: 0.7
            
    MDProgressBar:
        value: root.bar_value
        color: 1, 0.7, 0, 1
        size_hint_y: None
        height: "8dp"

# 3. Main Layout
MDBoxLayout:
    orientation: "vertical"

    MDBottomNavigation:
        panel_color: 0.1, 0.1, 0.1, 1
        selected_color_background: 0.2, 0.2, 0.2, 1
        text_color_active: 1, 0.7, 0, 1
        text_color_normal: 0.6, 0.6, 0.6, 1

        # --- TAB 1: INVENTORY ---
        MDBottomNavigationItem:
            name: 'screen_inventory'
            text: 'Inventory'
            icon: 'package-variant'

            MDBoxLayout:
                orientation: 'vertical'
                MDTopAppBar:
                    title: "Store Items"
                    md_bg_color: 0.15, 0.15, 0.15, 1
                    specific_text_color: 1, 1, 1, 1
                    elevation: 0
                
                ScrollView:
                    MDList:
                        id: container_items
                        padding: "10dp"
                        spacing: "10dp"

                MDFloatingActionButton:
                    icon: "plus"
                    pos_hint: {"center_x": .85, "center_y": .08}
                    on_release: app.show_add_item_dialog()
                    md_bg_color: 1, 0.7, 0, 1
                    text_color: 0, 0, 0, 1

        # --- TAB 2: SALES / CALENDAR ---
        MDBottomNavigationItem:
            name: 'screen_sales'
            text: 'Sales'
            icon: 'calendar'

            MDBoxLayout:
                orientation: 'vertical'
                MDTopAppBar:
                    title: "Daily Sales"
                    md_bg_color: 0.15, 0.15, 0.15, 1
                    right_action_items: [["calendar", lambda x: app.show_date_picker()]]
                
                MDBoxLayout:
                    size_hint_y: None
                    height: "50dp"
                    padding: "10dp"
                    md_bg_color: 0.12, 0.12, 0.12, 1
                    MDLabel:
                        id: date_label
                        text: "Today"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 0.9, 0.9, 0.9, 1
                        bold: True

                ScrollView:
                    MDList:
                        id: container_sales

                MDFloatingActionButton:
                    icon: "cart-plus"
                    pos_hint: {"center_x": .85, "center_y": .08}
                    on_release: app.show_add_sale_dialog()
                    md_bg_color: 1, 0.7, 0, 1
                    text_color: 0, 0, 0, 1

        # --- TAB 3: ANALYTICS ---
        MDBottomNavigationItem:
            name: 'screen_metrics'
            text: 'Metrics'
            icon: 'chart-bar'
            on_tab_press: app.update_analytics()

            MDBoxLayout:
                orientation: 'vertical'
                padding: "15dp"
                spacing: "15dp"
                md_bg_color: 0.05, 0.05, 0.05, 1

                # Top Stats Row
                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "90dp"
                    spacing: "15dp"
                    adaptive_width: True
                    pos_hint: {"center_x": .5}

                    StatCard:
                        title: "Total Revenue"
                        value: app.stat_revenue
                        color: (0, 0.8, 0, 1)
                    
                    StatCard:
                        title: "Total Profit"
                        value: app.stat_profit
                        color: (0.2, 0.6, 1, 1)

                MDSeparator:
                    height: "1dp"

                # Graph Toggle Buttons
                MDBoxLayout:
                    size_hint_y: None
                    height: "40dp"
                    spacing: "10dp"
                    adaptive_width: True
                    pos_hint: {"center_x": .5}
                    
                    MDRaisedButton:
                        text: "Monthly View"
                        md_bg_color: (0.3, 0.3, 0.3, 1) if app.graph_mode == 'year' else (1, 0.7, 0, 1)
                        text_color: (1,1,1,1) if app.graph_mode == 'year' else (0,0,0,1)
                        on_release: app.set_graph_mode('month')

                    MDRaisedButton:
                        text: "Yearly View"
                        md_bg_color: (0.3, 0.3, 0.3, 1) if app.graph_mode == 'month' else (1, 0.7, 0, 1)
                        text_color: (1,1,1,1) if app.graph_mode == 'month' else (0,0,0,1)
                        on_release: app.set_graph_mode('year')

                # The Graph List
                ScrollView:
                    MDList:
                        id: container_graph

<ContentAddItem>:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "280dp"

    MDTextField:
        id: item_name
        hint_text: "Item Name"
    MDTextField:
        id: item_weight
        hint_text: "Weight (kg/g)"
    MDTextField:
        id: item_cost
        hint_text: "Cost (Rp)"
        input_filter: "int"
    MDTextField:
        id: item_price
        hint_text: "Price (Rp)"
        input_filter: "int"

<ContentAddSale>:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "150dp"

    MDTextField:
        id: select_item
        hint_text: "Click to Select Item"
        on_focus: if self.focus: app.menu_items.open()
    MDTextField:
        id: sale_qty
        hint_text: "Quantity Sold"
        input_filter: "int"
'''

# --- CUSTOM WIDGET CLASSES ---
class StatCard(MDCard):
    title = StringProperty("")
    value = StringProperty("")
    color = ColorProperty([1, 1, 1, 1])

class GraphItem(MDBoxLayout):
    label_date = StringProperty("")
    label_value = StringProperty("")
    bar_value = NumericProperty(0)

class ContentAddItem(MDBoxLayout):
    pass

class ContentAddSale(MDBoxLayout):
    pass

class StoreApp(MDApp):
    current_date = date.today()
    dialog = None
    stat_revenue = StringProperty("Rp. 0")
    stat_profit = StringProperty("Rp. 0")
    graph_mode = StringProperty('month') 

    def build(self):
        # --- DARK THEME SETTINGS ---
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        
        # Database Setup
        self.conn = sqlite3.connect("store.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS items 
                            (id INTEGER PRIMARY KEY, name TEXT, weight TEXT, cost REAL, price REAL)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS sales 
                            (id INTEGER PRIMARY KEY, item_id INTEGER, date TEXT, qty INTEGER)""")
        self.conn.commit()

        return Builder.load_string(KV)

    def on_start(self):
        self.load_items()
        self.load_sales(self.current_date)

    def format_rp(self, value):
        return f"Rp. {value:,.0f}"

    # --- INVENTORY ---
    def load_items(self):
        self.root.ids.container_items.clear_widgets()
        self.cursor.execute("SELECT * FROM items")
        for item in self.cursor.fetchall():
            self.add_item_to_list(item)

    def add_item_to_list(self, item):
        text = f"[b]{item[1]}[/b] ({item[2]})"
        secondary = f"Buy: {self.format_rp(item[3])} | Sell: {self.format_rp(item[4])}"
        list_item = TwoLineAvatarIconListItem(text=text, secondary_text=secondary)
        list_item.add_widget(IconRightWidget(icon="trash-can-outline", 
                                           on_release=lambda x: self.delete_item(item[0])))
        self.root.ids.container_items.add_widget(list_item)

    def show_add_item_dialog(self):
        self.dialog = MDDialog(
            title="Add Item",
            type="custom",
            content_cls=ContentAddItem(),
            buttons=[
                MDFlatButton(text="CANCEL", on_release=self.close_dialog),
                MDRaisedButton(text="SAVE", on_release=self.save_item),
            ],
        )
        self.dialog.open()

    def save_item(self, obj):
        c = self.dialog.content_cls.ids
        if c.item_name.text and c.item_cost.text and c.item_price.text:
            self.cursor.execute("INSERT INTO items (name, weight, cost, price) VALUES (?, ?, ?, ?)",
                                (c.item_name.text, c.item_weight.text, float(c.item_cost.text), float(c.item_price.text)))
            self.conn.commit()
            self.load_items()
            self.close_dialog()
        else:
            toast("Please fill all fields")

    def delete_item(self, item_id):
        self.cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
        self.conn.commit()
        self.load_items()

    # --- SALES ---
    def show_date_picker(self):
        date_dialog = MDDatePicker(mode="picker")
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        self.current_date = value
        self.load_sales(value)

    def load_sales(self, date_val):
        self.root.ids.container_sales.clear_widgets()
        query = """SELECT sales.id, items.name, sales.qty, items.price 
                   FROM sales JOIN items ON sales.item_id = items.id 
                   WHERE sales.date = ?"""
        self.cursor.execute(query, (str(date_val),))
        total_day = 0
        for sale in self.cursor.fetchall():
            total = sale[2] * sale[3]
            total_day += total
            text = f"{sale[1]} (x{sale[2]})"
            secondary = f"{self.format_rp(total)}"
            li = TwoLineAvatarIconListItem(text=text, secondary_text=secondary)
            li.add_widget(IconRightWidget(icon="delete-outline", 
                                        on_release=lambda x, sid=sale[0]: self.delete_sale(sid)))
            self.root.ids.container_sales.add_widget(li)
        
        formatted_date = date_val.strftime("%d %B %Y")
        self.root.ids.date_label.text = f"{formatted_date}   |   Total: {self.format_rp(total_day)}"

    def show_add_sale_dialog(self):
        self.cursor.execute("SELECT id, name FROM items")
        items = self.cursor.fetchall()
        menu_items = [
            {"text": i[1], "viewclass": "OneLineListItem",
             "on_release": lambda x=i[1], y=i[0]: self.set_sale_item(x, y)} for i in items
        ]
        self.content_sale = ContentAddSale()
        self.menu_items = MDDropdownMenu(caller=self.content_sale.ids.select_item, items=menu_items, width_mult=4)
        
        self.dialog = MDDialog(
            title="Log Sale",
            type="custom",
            content_cls=self.content_sale,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=self.close_dialog),
                MDRaisedButton(text="ADD", on_release=self.save_sale),
            ],
        )
        self.selected_item_id = None
        self.dialog.open()

    def set_sale_item(self, text, i_id):
        self.content_sale.ids.select_item.text = text
        self.selected_item_id = i_id
        self.menu_items.dismiss()

    def save_sale(self, obj):
        qty = self.content_sale.ids.sale_qty.text
        if self.selected_item_id and qty:
            self.cursor.execute("INSERT INTO sales (item_id, date, qty) VALUES (?, ?, ?)",
                                (self.selected_item_id, str(self.current_date), int(qty)))
            self.conn.commit()
            self.load_sales(self.current_date)
            self.close_dialog()

    def delete_sale(self, sale_id):
        self.cursor.execute("DELETE FROM sales WHERE id=?", (sale_id,))
        self.conn.commit()
        self.load_sales(self.current_date)

    def close_dialog(self, *args):
        if self.dialog: self.dialog.dismiss()

    # --- ANALYTICS ---
    def set_graph_mode(self, mode):
        self.graph_mode = mode
        self.update_analytics()

    def update_analytics(self):
        query = "SELECT items.cost, items.price, sales.qty FROM sales JOIN items ON sales.item_id = items.id"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        rev, prof = 0, 0
        for cost, price, qty in data:
            rev += price * qty
            prof += (price - cost) * qty
        self.stat_revenue = self.format_rp(rev)
        self.stat_profit = self.format_rp(prof)

        self.root.ids.container_graph.clear_widgets()
        fmt = '%Y-%m' if self.graph_mode == 'month' else '%Y'
        query_graph = f"""SELECT strftime('{fmt}', date) as period, SUM(items.price * sales.qty)
                          FROM sales JOIN items ON sales.item_id = items.id
                          GROUP BY period ORDER BY period DESC"""
        self.cursor.execute(query_graph)
        rows = self.cursor.fetchall()

        if not rows: return
        max_val = max([r[1] for r in rows]) if rows else 1

        for period, amount in rows:
            percent = (amount / max_val) * 100
            display_date = period if self.graph_mode == 'month' else f"Year {period}"
            
            # Using Factory to create the now fully defined Python class
            item = Factory.GraphItem()
            item.label_date = display_date
            item.label_value = self.format_rp(amount)
            item.bar_value = percent
            self.root.ids.container_graph.add_widget(item)

if __name__ == '__main__':
    StoreApp().run()