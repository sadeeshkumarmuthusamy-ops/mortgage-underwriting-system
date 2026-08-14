from src.config.settings import Settings


def test_settings_loads_values_from_env_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=test-key\nOPENAI_LLM_MODEL=gpt-4.1\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    settings = Settings(_env_file=env_file)

    assert settings.OPENAI_API_KEY == "test-key"
    assert settings.OPENAI_LLM_MODEL == "gpt-4.1"
