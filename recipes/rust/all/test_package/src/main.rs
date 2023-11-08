use serde::Serialize;

#[derive(Serialize)]
struct Hello {
    message: String,
}

fn main() {
    let greeting = Hello {
        message: String::from("Hi!"),
    };
    let serialized = serde_json::to_string(&greeting).unwrap();
    println!("{}", serialized);
}
