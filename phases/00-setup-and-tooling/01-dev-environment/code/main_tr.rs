// Orijinal: https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/01-dev-environment/code/main.rs
// Bu dosya, orijinal kodun Türkçe çevrilmiş versiyonudur.

use std::process::{Command, ExitCode};

struct Check {
    name: &'static str,
    program: &'static str,
    args: &'static [&'static str],
    optional: bool,
}

const CHECKS: &[Check] = &[
    Check { name: "Git",         program: "git",    args: &["--version"], optional: false },
    Check { name: "Python 3.10+", program: "python3", args: &["--version"], optional: false },
    Check { name: "Node.js",     program: "node",   args: &["--version"], optional: false },
    Check { name: "Rust (rustc)", program: "rustc",  args: &["--version"], optional: false },
    Check { name: "Cargo",       program: "cargo",  args: &["--version"], optional: false },
    Check { name: "uv (Python)", program: "uv",     args: &["--version"], optional: true },
    Check { name: "pnpm",        program: "pnpm",   args: &["--version"], optional: true },
    Check { name: "Julia",       program: "julia",  args: &["--version"], optional: true },
];

fn run_check(check: &Check) -> Result<String, String> {
    let output = Command::new(check.program)
        .args(check.args)
        .output()
        .map_err(|e| format!("{}: {}", check.program, e))?;

    if !output.status.success() {
        return Err(format!("çıkış kodu {:?}", output.status.code()));
    }

    let combined = if !output.stdout.is_empty() {
        &output.stdout
    } else {
        &output.stderr
    };

    let raw = String::from_utf8_lossy(combined);
    let line = raw.lines().next().unwrap_or("").trim().to_string();
    if line.is_empty() {
        Err("boş sürüm çıktısı".to_string())
    } else {
        Ok(line)
    }
}

fn parse_minor_python(version_line: &str) -> Option<(u32, u32)> {
    let trimmed = version_line.trim_start_matches("Python").trim();
    let mut parts = trimmed.split('.');
    let major: u32 = parts.next()?.parse().ok()?;
    let minor: u32 = parts.next()?.parse().ok()?;
    Some((major, minor))
}

fn print_header() {
    println!();
    println!("=== Sıfırdan Yapay Zeka Mühendisliği — Ortam Kontrolü (Rust) ===");
    println!();
    println!("1. Katman (sistem) -> 2. Katman (paket yöneticileri) -> 3. Katman (çalışma zamanları) -> 4. Katman (kütüphaneler)");
    println!();
}

fn main() -> ExitCode {
    print_header();

    let mut required_pass = 0u32;
    let mut required_total = 0u32;
    let mut optional_pass = 0u32;
    let mut optional_total = 0u32;

    let mut python_ok = true;

    println!("Zorunlu araçlar:");
    for check in CHECKS.iter().filter(|c| !c.optional) {
        required_total += 1;
        match run_check(check) {
            Ok(version) => {
                if check.name.starts_with("Python") {
                    match parse_minor_python(&version) {
                        Some((major, minor)) if (major, minor) >= (3, 10) => {}
                        _ => {
                            println!("  [KALDI] {:<14} {} (Python 3.10+ gerekli)", check.name, version);
                            python_ok = false;
                            continue;
                        }
                    }
                }
                required_pass += 1;
                println!("  [GEÇTİ] {:<14} {}", check.name, version);
            }
            Err(why) => {
                println!("  [KALDI] {:<14} {}", check.name, why);
                if check.name.starts_with("Python") {
                    python_ok = false;
                }
            }
        }
    }

    println!();
    println!("İsteğe bağlı araçlar:");
    for check in CHECKS.iter().filter(|c| c.optional) {
        optional_total += 1;
        match run_check(check) {
            Ok(version) => {
                optional_pass += 1;
                println!("  [GEÇTİ] {:<14} {}", check.name, version);
            }
            Err(_) => {
                println!("  [atla] {:<14} yüklü değil", check.name);
            }
        }
    }

    println!();
    println!("Özet: {}/{} zorunlu, {}/{} isteğe bağlı",
             required_pass, required_total, optional_pass, optional_total);

    if required_pass == required_total && python_ok {
        println!();
        println!("Ortam hazır. Faz 1 ile başlayın.");
        ExitCode::SUCCESS
    } else {
        println!();
        println!("Yukarıdaki başarısız kontrolleri düzeltin, sonra bunu tekrar çalıştırın.");
        ExitCode::from(1)
    }
}
