import streamlit as st
import sqlite3
import os  # Add this import
from datetime import datetime, timedelta  # 添加timedelta导入
from config import *

# 在文件顶部添加配置
MAX_DISPLAY_WIDTH = 400  # 调整为更合理的显示宽度
MAX_DISPLAY_HEIGHT = 300  # 调整为更合理的显示高度
# 初始化数据库
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  due_date TEXT,
                  details TEXT,
                  picture BLOB,
                  attachment TEXT,
                  remark TEXT DEFAULT 'open',
                  category TEXT)''')
    # 添加users表
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# 获取所有任务
# 获取所有任务（按category分组）
def get_tasks():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, name, due_date, remark, category FROM tasks WHERE remark != 'closed' ORDER BY category, due_date")
    tasks = c.fetchall()
    conn.close()
    return tasks

# 更新任务状态为closed
def close_task(task_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE tasks SET remark = 'closed' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# 获取任务详情
def get_task_details(task_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT details, picture, attachment FROM tasks WHERE id = ?", (task_id,))
    details = c.fetchone()
    conn.close()
    return details

# 添加登录验证函数
def authenticate(username, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # 新增处理逻辑：去除前后空格并转换为小写
    processed_username = username.strip().lower()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
             (processed_username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

# 主应用
def main():
    # 检查cookie中的登录状态
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # 登录表单
    if not st.session_state.logged_in:
        with st.form("login_form"):
            st.subheader("系统登录")
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            submitted = st.form_submit_button("登录")
            if submitted:
                if authenticate(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("登录成功!")
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
        return  # 未登录时不显示主界面
    
    st.title("任务管理系统")
    
    # 添加分类标签样式
    st.markdown("""
    <style>
    h3 {
        background-color: var(--secondary-background-color);
        color: #1E90FF !important;
        padding: 5px 10px;
        border-radius: 5px;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
        line-height: 1.2;
        font-size: 1rem !important;
        border: 1px solid var(--border-color);
    }
    /* 新增按钮样式 */
    div[data-testid="column"] {
        min-width: 0 !important;
        padding: 0 0.2rem !important;
    }
    button[kind="secondary"] {
        padding: 0.05rem 0.05rem !important;
        font-size: 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

        # 添加分类标签样式
    st.markdown("""
    <style>
    h3 {
        background-color: var(--secondary-background-color);
        color: #1E90FF !important;
        padding: 5px 10px;
        border-radius: 5px;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
        line-height: 1.2;
        font-size: 1rem !important;
        border: 1px solid var(--border-color);
    }
    /* 新增顶部按钮容器样式 */
    div[data-testid="column"] {
        min-width: 0 !important;
        padding: 0 0.2rem !important;
        flex: 1 0 auto !important;
    }
    .stButton > button {
        width: 100% !important;
        min-width: 60px !important;
        white-space: nowrap !important;
        padding: 0.25rem 0.5rem !important;
        font-size: 0.8rem !important;
    }
    @media (max-width: 768px) {
        div[data-testid="column"] {
            flex: 1 0 25% !important;
            max-width: 25% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 初始化会话状态
    if 'show_new_task' not in st.session_state:
        st.session_state.show_new_task = False
    if 'show_edit_task' not in st.session_state:
        st.session_state.show_edit_task = False
    if 'edit_task_id' not in st.session_state:
        st.session_state.edit_task_id = None
    
    # 创建上传目录
    os.makedirs("uploads/picture", exist_ok=True)
    os.makedirs("uploads/attachment", exist_ok=True)

    # 顶部按钮
    col1, col2, col3, col4 = st.columns(4)  # 改为4列
    with col1:
        if st.button("➕New"):
            st.session_state['show_new_task'] = not st.session_state.get('show_new_task', False)
            st.session_state['show_edit_task'] = False
            st.session_state['show_closed_items'] = False

    # 退出登录
    with col4:
        if st.button(f"👋 {st.session_state.get('username', '')} "):
            st.session_state.logged_in = False
            st.rerun()

    # 新建任务表单
    if st.session_state.get('show_new_task'):
        with st.container():
            st.markdown(
                """
                <style>
                div[data-testid="stForm"] {
                    border: 2px solid red;
                    border-radius: 5px;
                    padding: 20px;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            with st.form("new_task_form"):
                name = st.text_input("任务名称*", max_chars=100)
                due_date = st.date_input("截止日期", value=datetime.now().date() + timedelta(days=14))  # 修改为2周后
                details = st.text_area("任务详情")
                group = st.selectbox("任务分组", options=groups)  # 添加分组选择框
                
                # 图片上传
                picture = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"], key="picture_uploader")
                picture_path = None
                if picture:
                    picture_path = f"uploads/picture/{picture.name}"
                    with open(picture_path, "wb") as f:
                        f.write(picture.getbuffer())
                
                # 附件上传
                attachment = st.file_uploader("上传附件", type=["pdf", "docx", "xlsx"], key="attachment_uploader")
                attachment_path = None
                if attachment:
                    attachment_dir = os.path.abspath("uploads/attachment")
                    os.makedirs(attachment_dir, exist_ok=True)
                    attachment_path = os.path.join(attachment_dir, attachment.name)
                    with open(attachment_path, "wb") as f:
                        f.write(attachment.getbuffer())
                
                submitted = st.form_submit_button("保存")
                if submitted and name:
                    # 更新数据库插入语句，包含group字段
                    conn = sqlite3.connect('database.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO tasks (name, due_date, details, picture, attachment, remark, category) VALUES (?, ?, ?, ?, ?, 'open', ?)",
                             (name, str(due_date), details, picture_path, attachment_path, group))
                    conn.commit()
                    conn.close()
                    st.success("任务创建成功!")
                    st.session_state['show_new_task'] = False
                    st.rerun()
                elif submitted:
                    st.error("请填写任务名称!")

    # 编辑任务表单
    if st.session_state.get('show_edit_task'):
        task_id = st.session_state.get('edit_task_id')
        if task_id:
            # 获取当前任务详情，包含category字段
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("SELECT name, due_date, details, picture, attachment, remark, category FROM tasks WHERE id = ?", (task_id,))
            task_data = c.fetchone()
            conn.close()
            
            if task_data:
                with st.container():
                    st.markdown(
                        """
                        <style>
                        div[data-testid="stForm"] {
                            border: 2px solid blue;
                            border-radius: 5px;
                            padding: 20px;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                    with st.form("edit_task_form"):
                        current_name, current_due_date, current_details, current_picture, current_attachment, current_remark, current_category = task_data
                        
                        new_name = st.text_input("任务名称*", value=current_name, max_chars=100)
                        new_due_date = st.date_input("截止日期", value=datetime.strptime(current_due_date, "%Y-%m-%d").date() if current_due_date else None)
                        new_details = st.text_area("任务详情", value=current_details)
                        
                        # 添加分组选择框
                        new_category = st.selectbox("任务分组", options=groups, index=groups.index(current_category) if current_category in groups else 0)
                        
                        # 图片上传
                        new_picture = st.file_uploader("更新图片", type=["png", "jpg", "jpeg"], key=f"edit_picture_{task_id}")
                        new_picture_path = current_picture
                        if new_picture:
                            new_picture_path = f"uploads/picture/{new_picture.name}"
                            with open(new_picture_path, "wb") as f:
                                f.write(new_picture.getbuffer())
                        
                        # 附件上传
                        new_attachment = st.file_uploader("更新附件", type=["pdf", "docx", "xlsx"], key=f"edit_attachment_{task_id}")
                        new_attachment_path = current_attachment
                        if new_attachment:
                            attachment_dir = os.path.abspath("uploads/attachment")
                            os.makedirs(attachment_dir, exist_ok=True)
                            new_attachment_path = os.path.join(attachment_dir, new_attachment.name)
                            with open(new_attachment_path, "wb") as f:
                                f.write(new_attachment.getbuffer())
                        
                        # 添加remark选择框
                        new_remark = st.selectbox("任务状态", options=["open", "closed"], index=0 if current_remark == "open" else 1)
                        
                        submitted = st.form_submit_button("保存修改")
                        if submitted and new_name:
                            # 更新数据库，包含category字段
                            conn = sqlite3.connect('database.db')
                            c = conn.cursor()
                            c.execute("UPDATE tasks SET name=?, due_date=?, details=?, picture=?, attachment=?, remark=?, category=? WHERE id=?",
                                     (new_name, str(new_due_date), new_details, new_picture_path, new_attachment_path, new_remark, new_category, task_id))
                            conn.commit()
                            conn.close()
                            st.success("任务修改成功!")
                            st.session_state['show_edit_task'] = False
                            st.rerun()
                        elif submitted:
                            st.error("请填写任务名称!")

    with col2:
        if st.button("👉Open"):
            st.session_state['show_closed_items'] = False
            st.session_state['show_new_task'] = False
            st.session_state['show_edit_task'] = False
    with col3:
        if st.button("✅Closed"):
            st.session_state['show_closed_items'] = True
            st.session_state['show_new_task'] = False
            st.session_state['show_edit_task'] = False

    # 显示已完成任务
    if st.session_state.get('show_closed_items'):
        st.subheader("已完成任务")
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id, name, due_date, remark FROM tasks WHERE remark = 'closed'")
        closed_tasks = c.fetchall()
        conn.close()
        
        if closed_tasks:
            for task in closed_tasks:
                task_id, name, due_date, remark = task
                # 计算日期差异
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date() if due_date else None
                today = datetime.now().date()
                days_diff = (due_date_obj - today).days if due_date_obj else float('inf')
                
                # 构建标题
                title = f"✅ {task_id}: {name[:20]}{' '*(25-len(name))} (Due: {due_date})"
                
                with st.expander(title, expanded=False):
                    details = get_task_details(task_id)
                    if details:
                        st.write("Details:", details[0])
                        
                        if details[1]:  # 图片
                            try:
                                st.image(details[1], 
                                       caption="Task Picture",
                                       width=MAX_DISPLAY_WIDTH)
                            except st.runtime.media_file_storage.MediaFileStorageError:
                                st.warning("Image NA")
                        
                        # 按钮区域
                        col1, col2 = st.columns(2)
                        with col1:
                            if details[2] and os.path.exists(details[2]):  # 仅当附件存在时显示下载按钮
                                with open(details[2], "rb") as f:
                                    st.download_button(
                                        label="下载附件",
                                        data=f,
                                        file_name=os.path.basename(details[2]),
                                        mime="application/octet-stream"
                                    )
                        with col2:
                            if st.button("Reopen Task", key=f"reopen_{task_id}"):
                                conn = sqlite3.connect('database.db')
                                c = conn.cursor()
                                c.execute("UPDATE tasks SET remark = 'open' WHERE id = ?", (task_id,))
                                conn.commit()
                                conn.close()
                                st.rerun()
                        
                        if details[2] and not os.path.exists(details[2]):  # 附件不存在时显示警告
                            st.warning("附件文件不存在")
        else:
            st.write("暂无已完成任务")
    else:
        # 获取并显示未完成任务列表（按category分组）
        tasks = get_tasks()
        current_category = None
        
        for task in tasks:
            task_id, name, due_date, remark, category = task
            
            # 显示分类标题
            display_category = category if category else "NA Category"
            if display_category != current_category:
                current_category = display_category
                st.markdown(f"### 🏷️ {display_category}")
            
            # 计算日期差异
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date() if due_date else None
            today = datetime.now().date()
            days_diff = (due_date_obj - today).days if due_date_obj else float('inf')
            
            # 构建标题
            if days_diff < 7:
                title = f"🔥 {task_id}: {name[:20]}{' '*(25-len(name))} (Due: {due_date})"
            elif days_diff < 14:
                title = f"⏰ {task_id}: {name[:20]}{' '*(25-len(name))} (Due: {due_date})"
            else:
                title = f"{task_id}: {name[:20]}{' '*(25-len(name))} (Due: {due_date})"
            
            with st.expander(title, expanded=False):
                details = get_task_details(task_id)
                if details:
                    st.write("Details:", details[0])
                    
                    if details[1]:  # 图片
                        try:
                            st.image(details[1], 
                                   caption="Task Picture",
                                   width=MAX_DISPLAY_WIDTH)
                        except st.runtime.media_file_storage.MediaFileStorageError:
                            st.warning("Image NA")
                    
                    # 按钮区域
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if details[2] and os.path.exists(details[2]):  # 仅当附件存在时显示下载按钮
                            with open(details[2], "rb") as f:
                                st.download_button(
                                    label="下载附件",
                                    data=f,
                                    file_name=os.path.basename(details[2]),
                                    mime="application/octet-stream"
                                )
                    with col2:
                        if st.button("Close Task", key=f"close_{task_id}"):
                            close_task(task_id)
                            st.rerun()
                    with col3:
                        if st.button("Change Task", key=f"change_{task_id}"):
                            # 打开编辑窗口时关闭新建窗口
                            st.session_state['edit_task_id'] = task_id
                            st.session_state['show_edit_task'] = True
                            st.session_state['show_new_task'] = False
                
                    if details[2] and not os.path.exists(details[2]):  # 附件不存在时显示警告
                        st.warning("附件文件不存在")
                # 移除下面重复的Close Task按钮

if __name__ == "__main__":
    main()