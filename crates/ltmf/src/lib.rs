use ftml::tree::{Element, Container, ContainerType};


pub fn to_wikitext(elements: &[Element]) -> String {
    elements
        .iter()
        .map(|el| element_to_string(el))
        .collect::<Vec<String>>()
        .join("")
}


fn element_to_string(el: &Element) -> String {
    match el {
        // 1. 处理纯文本
        Element::Text(t) => t.to_string(),

        // 2. 处理容器（加粗、斜体、div 等）
        Element::Container(c) => container_to_string(c),

        // 3. 处理原子元素
        Element::LineBreak => "\n".to_string(),
        Element::HorizontalRule => "\n----\n".to_string(),

        // 4. 剩下的先用占位符，免得编译器报错
        _ => format!("/* 暂未实现的元素: {:?} */", el),
    }
}


fn container_to_string(c: &Container) -> String {
    // 递归调用：先拿到容器内部的内容
    let inner = to_wikitext(&c.elements);

    match &c.container_type {
        ContainerType::Bold => format!("**{}**", inner),
        ContainerType::Italics => format!("//{}//", inner),
        ContainerType::Underline => format!("__{}__", inner),
        ContainerType::Strikethrough => format!("--{}--", content),

        // 特殊处理 [[div]]
        ContainerType::Div { attributes } => {
            // 这里以后可以根据 attributes 解析 class 和 styles
            format!("[[div]]\n{}\n[[/div]]", inner)
        },

        // 兜底：如果不知道是什么容器，就直接吐出里面的内容
        _ => inner,
    }
}