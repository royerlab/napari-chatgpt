# Test Review: Core Modules & Untested Packages

## Summary

This review examines test coverage across the six most critical areas of the napari-chatgpt codebase: the omega_agent core, the llm package, the chat_server, the root widget, the microplugin package, and the utils/qt package. The findings reveal that the vast majority of the project's architectural backbone has **zero unit tests**. Out of approximately 25 source files reviewed, only **one file** (`api_key_vault.py`) has a dedicated test. The rest of the core infrastructure -- the agent orchestration, the thread-safe napari bridge, the WebSocket chat server, the plugin widget, the entire microplugin code editor, and all Qt utility dialogs -- operate entirely without automated test coverage.

| Area | Source Files Reviewed | Files With Tests | Coverage Assessment |
|------|----------------------|------------------|---------------------|
| omega_agent/ core | 4 | 0 | **None** |
| llm/ package | 5 | 1 (partial) | **Minimal** |
| chat_server/ | 2 | 0 | **None** |
| _widget.py | 1 | 0 | **None** |
| microplugin/ | 6 | 0 | **None** |
| utils/qt/ | 4 | 0 | **None** |

---

## Completely Untested Modules (Critical Gap)

### 1. omega_agent/omega_agent.py -- The Agent Class
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/omega_agent.py`
- **Tests**: None.
- **What it does**: Defines OmegaAgent, the central class extending litemind.agent.Agent. It accepts an API, model name, temperature, and toolset.
- **Risk**: While the class is currently a thin wrapper around the parent Agent, any future business logic added here will be completely unverified. There is no test that verifies the agent can be instantiated, that constructor parameters are correctly passed through, or that the inheritance chain functions properly.

### 2. omega_agent/napari_bridge.py -- Thread-Safe Queue Communication
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/napari_bridge.py`
- **Tests**: None.
- **What it does**: Implements the critical NapariBridge class that uses Queue objects and napari thread_worker decorator to safely execute LLM-generated code on the Qt event loop. Contains _execute_in_napari_context() with a 300-second timeout, get_viewer_info(), take_snapshot(), and thread-safe global viewer info accessors (_set_viewer_info, _get_viewer_info).
- **Risk**: **Critical**. This is the most dangerous untested module. The NapariBridge is the sole mechanism through which LLM-generated code reaches the napari viewer. Bugs here could cause deadlocks (queue operations with no timeout on to_napari_queue.put), race conditions (the global _viewer_info accessed across threads), silent failures (exceptions caught and returned as strings rather than raised), and resource leaks (the worker thread runs in an infinite loop with no cleanup mechanism beyond a None sentinel).

### 3. omega_agent/omega_init.py -- Agent Initialization and Toolset Assembly
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/omega_init.py`
- **Tests**: None.
- **What it does**: Contains initialize_omega_agent() which orchestrates the full agent setup: creates LLMs, assembles the toolset (all napari tools, search tools, vision tools), configures system prompts with personality and didactic modes, and checks model feature support. Also contains prepare_toolset() and _append_all_napari_tools().
- **Risk**: **High**. This is the integration point where all components come together. There are no tests verifying that all tools are correctly instantiated, that system prompts are correctly formatted, that model feature checks correctly gate tool inclusion, or that the _append_basic_tools() function (which appears to be dead code, never called) is handled correctly.

### 4. omega_agent/prompts.py -- System Prompts and Personalities
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/prompts.py`
- **Tests**: None.
- **What it does**: Defines the SYSTEM prompt template with {personality} and {didactics} placeholders, the PERSONALITY dictionary mapping personality names to descriptions, and the DIDACTICS string.
- **Risk**: **Medium**. Though this is mostly static data, there are no tests verifying that all personality keys used in _widget.py exist in the PERSONALITY dict, or that template placeholders in SYSTEM match what omega_init.py passes.

### 5. chat_server/chat_server.py -- WebSocket Server
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/chat_server/chat_server.py`
- **Tests**: None.
- **What it does**: Implements NapariChatServer, a FastAPI WebSocket server that manages conversations between the user and the Omega agent. Contains WebSocket handlers, async/sync bridging (sync_handler, async_run_in_executor), notification functions for tool lifecycle events, Jinja2 template rendering, and the start_chat_server() factory function.
- **Risk**: **Critical**. This is 537 lines of complex async/sync code with WebSocket connection management with no test for disconnect handling, an event_loop instance variable that is None until the first WebSocket connects with no guard against calling sync_handler before that, notify_user_omega_tool_activity that raises ValueError for unknown activity types (never tested), and the start_chat_server() function that spawns threads, opens browsers, and has a polling loop.

### 6. chat_server/chat_response.py -- Chat Response Schema
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/chat_server/chat_response.py`
- **Tests**: None.
- **What it does**: Defines a simple ChatResponse dataclass with sender, message, type fields and a dict() method.
- **Risk**: **Low** for this simple class, but the custom dict() method shadows Python built-in and could cause confusion.

### 7. _widget.py -- napari Plugin Entry Point
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/_widget.py`
- **Tests**: None.
- **What it does**: Defines OmegaQWidget, the main napari plugin widget with ~590 lines of UI setup: model selection combos, checkbox configurations, the Start Omega button handler that creates NapariChatServer instances, and the Show Editor button. Contains _preferred_models() static method for model sorting.
- **Risk**: **High**. This is the user-facing entry point. Untested aspects include _preferred_models() sorting logic (static method that mutates the input list), _creativity_mapping dictionary lookup (KeyError if unexpected value), _start_omega() error handling and server lifecycle, close() method cleanup, and connection to viewer destroyed signal.

### 8. microplugin/microplugin_window.py -- Singleton Code Editor Window
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/microplugin/microplugin_window.py`
- **Tests**: None.
- **What it does**: Implements MicroPluginMainWindow with a custom singleton pattern via __new__/__init__, inherits from CodeSnippetEditorWindow, manages folder paths, window sizing, and the static add_snippet() method.
- **Risk**: **High**. The singleton pattern is complex and fragile. _singleton_pattern_active is a class variable toggled externally. add_snippet() accesses _singleton_instance directly without null check.

### 9. microplugin/formating/black_formating.py -- Code Formatting
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/microplugin/formating/black_formating.py`
- **Tests**: None.
- **What it does**: format_code(code) and format_file(file_path) using Black. Both silently catch all exceptions and return the original code/do nothing.
- **Risk**: **Medium**. Silent failure means formatting errors are invisible.

### 10. microplugin/code_editor/python_syntax_highlighting.py -- Syntax Highlighter
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/microplugin/code_editor/python_syntax_highlighting.py`
- **Tests**: None.
- **What it does**: Implements PythonSyntaxHighlighter extending QSyntaxHighlighter with keyword, operator, brace, string, comment, and number highlighting, plus multi-line string support.
- **Risk**: **Low-Medium**. Syntax highlighting bugs are cosmetic but affect user experience. Uses QRegExp which is deprecated in Qt6.

### 11. microplugin/code_editor/python_code_editor_widget.py -- Code Editor Widget
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/microplugin/code_editor/python_code_editor_widget.py`
- **Tests**: None.
- **What it does**: Implements PythonCodeEditor extending QPlainTextEdit with Jedi-based code completion, auto-indentation, and undoable text replacement.
- **Risk**: **Medium**. The auto-indentation logic in keyPressEvent is naive (uses any(kw in line ...) which would match "definition" for "def").

### 12. microplugin/network/code_drop_server.py -- Network Code Sharing Server
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/microplugin/network/code_drop_server.py`
- **Tests**: None.
- **What it does**: UDP multicast server for broadcasting presence and TCP server for receiving code from other instances. Uses QThread workers for both broadcasting and receiving.
- **Risk**: **Medium-High**. The _find_port() method has a potential infinite loop if all ports 5000-5100 are occupied.

### 13. microplugin/network/code_drop_client.py -- Network Code Sharing Client
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/microplugin/network/code_drop_client.py`
- **Tests**: None.
- **What it does**: Discovers servers via multicast, sends code via TCP sockets. Contains a nested SendWorker class created dynamically in create_send_worker().
- **Risk**: **Medium-High**. The send_message_by_address() method has a retry loop that could block the thread. The dynamically created SendWorker class captures parent_self via closure.

### 14. utils/qt/package_dialog.py -- Package Installation Dialog
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/qt/package_dialog.py`
- **Tests**: None.
- **What it does**: Qt dialog for confirming package installations.
- **Risk**: **Medium**. The thread-safe variant install_packages_dialog_threadsafe() appears broken: it calls run_on_main_thread() which schedules the dialog asynchronously via QTimer.singleShot(0, func) but never captures or returns the result.

### 15. utils/qt/qt_app.py -- Qt Application Helper
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/qt/qt_app.py`
- **Tests**: None.
- **What it does**: get_or_create_qt_app() and run_on_main_thread() -- Qt application lifecycle helpers.
- **Risk**: **Low**.

### 16. utils/qt/one_time_disclaimer_dialog.py -- Disclaimer Dialog
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/qt/one_time_disclaimer_dialog.py`
- **Tests**: None.
- **What it does**: Shows a one-time disclaimer using QMessageBox, persisting acknowledgment via AppConfiguration.
- **Risk**: **Low-Medium**.

### 17. utils/qt/download_file_qt.py -- File Download Dialog
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/qt/download_file_qt.py`
- **Tests**: None.
- **What it does**: Qt dialog with progress bar for downloading files, using a QThread-based DownloadWorker.
- **Risk**: **Medium**. The DownloadWorker.run() method deletes partially downloaded files on exceptions without checking if the file exists first.

---

## Partially Tested Modules

### llm/api_keys/api_key_vault.py -- Encrypted Key Storage
- **File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/llm/api_keys/api_key_vault.py`
- **Test file**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/llm/api_keys/test/api_key_vault_test.py`
- **Test coverage**: Partial. Tests cover base64 encode/decode roundtrip, full write/read cycle with correct password, wrong password raises exception, and clear_key()/is_key_present() behavior.
- **What is missing**:
  - No test for legacy salt backward compatibility (the _LEGACY_SALT path when "salt" key is absent from JSON)
  - No test for file corruption or malformed JSON
  - No test for concurrent access to the key file
  - No test that verifies salt uniqueness across multiple writes
  - No cleanup of the "dummy" key file in the default ~/.omega_api_keys/ directory after tests (test leaves artifacts)

---

## Risk Assessment

### Severity: Critical (Immediate Risk)

1. **NapariBridge** (napari_bridge.py): The queue-based communication is the single point of failure for all LLM-to-napari interactions. A deadlock here freezes the entire application. The 300-second timeout on from_napari_queue.get() is only on the response side; to_napari_queue.put() has no timeout and will block indefinitely if the queue is full (maxsize=16).

2. **NapariChatServer** (chat_server.py): The WebSocket server manages the entire user interaction loop. The event_loop being None until the first WebSocket connects means sync_handler() will raise AttributeError if called before a client connects. No test verifies this state machine.

3. **BaseNapariTool** (base_napari_tool.py): While not in the original review scope, this 350-line class orchestrates code generation, preparation, execution, and error recovery. It has zero tests and contains the critical _run_code_catch_errors_fix_and_try_again recursive retry logic.

### Severity: High (Significant Risk)

4. **omega_init.py**: The agent initialization is the only integration test target. If tool instantiation fails silently, the agent operates with a degraded toolset and the user has no indication.

5. **OmegaQWidget** (_widget.py): The plugin entry point. A crash here prevents the entire plugin from loading in napari.

6. **MicroPluginMainWindow**: The singleton pattern is error-prone. If the class variable state gets corrupted, the editor becomes inaccessible.

### Severity: Medium

7. **Network code sharing** (code_drop_server/client): Port conflicts, multicast failures, and thread lifecycle issues could cause hangs or crashes.

8. **Black formatting**: Silent exception swallowing masks genuine errors.

9. **Package dialog**: install_packages_dialog_threadsafe() appears to be non-functional (return value is discarded).

### Severity: Low

10. **ChatResponse**: Simple dataclass, low risk of defects.
11. **qt_app.py**: Trivial utility functions.
12. **Prompts**: Static data with no logic.

---

## Weak Tests (In Modules That Have Tests)

### api_key_vault_test.py

```python
# File: src/napari_chatgpt/llm/api_keys/test/api_key_vault_test.py

def test_api_key_vault():
    api_key = "APIKEY123456789"
    key_vault = KeyVault("dummy")
    key_vault.clear_key()
    assert not key_vault.is_key_present()
    encrypted_key = key_vault.write_api_key(api_key, "1234")
    # ...
    try:
        wrong_api_key = key_vault.read_api_key("12345")
        assert not wrong_api_key == api_key
        assert False
    except Exception:
        assert True
```

**Issues**:
1. **Overly broad exception catching**: The test catches Exception instead of cryptography.fernet.InvalidToken. This means any unrelated exception would also pass the test.
2. **No test cleanup**: The test creates a file at ~/.omega_api_keys/dummy.json but never cleans it up. This leaves artifacts in the developer home directory.
3. **No parameterized tests**: Only tests one password, one key. No edge cases (empty string password, very long key, Unicode characters, special characters in password).
4. **Missing legacy salt test**: The vault has a backward-compatibility code path for keys written with _LEGACY_SALT (before per-key random salts were introduced). This path is completely untested.
5. **print() in tests**: The test uses print(encrypted_key) and print(correct_api_key) -- these should use assertions or logging.

### Omega Agent Tools Tests (Adjacent but Relevant)

The tools in omega_agent/tools/ have some tests, but they are shallow:

- **functions_info_tests.py**: Tests one tool with two queries. No mock, directly calls the tool which depends on skimage being installed.
- **web_search_tool_tests.py**: Single test that calls DuckDuckGo. Flaky due to external dependency.
- **wikipedia_search_tool_tests.py**: Better -- wraps in try/except for DuckDuckGoSearchException and uses pytest.skip. Still only one query tested.
- **file_open_tool_test.py** and **image_denoising_tool_test.py**: Only test source code inspection (string matching on inspect.getsource()), not actual tool behavior.
- **utils_test.py** (delegated_code): Good structural tests for utility functions but no integration tests.

---

## Recommendations

### Priority 1: Add Tests for NapariBridge (Critical)

The NapariBridge is testable without a real napari viewer using mocks. Key test cases:
- Verify that _execute_in_napari_context returns a timeout message after the timeout period
- Verify that ExceptionGuard responses are correctly converted to error strings
- Verify that the None sentinel correctly stops the worker loop
- Verify thread-safety of _get_viewer_info / _set_viewer_info under concurrent access
- Test that to_napari_queue.put() blocks when queue is full (maxsize=16)

### Priority 2: Add Tests for Chat Server Core Logic

The NapariChatServer inner functions can be tested by extracting them into standalone functions:
- send_final_response_to_user can be tested with a mock WebSocket
- notify_user_omega_* functions can be tested for correct ChatResponse construction
- ChatResponse.dict() should have a basic serialization test

### Priority 3: Add Tests for omega_init.py Toolset Assembly

- Test that prepare_toolset() returns a toolset with the expected number of tools
- Test that _append_all_napari_tools() adds all expected tools
- Test that dead code (_append_basic_tools) is either tested or removed
- Test that initialize_omega_agent() correctly formats system prompts

### Priority 4: Add Tests for the Widget

- Test _preferred_models() static method with various model lists
- Test _creativity_mapping coverage
- Test close() cleanup behavior

### Priority 5: Add Tests for MicroPlugin Singleton

- Test that the singleton pattern works correctly
- Test that add_snippet() handles the case where _singleton_instance is None
- Test format_code() and format_file() with valid and invalid Python code

### Priority 6: Fix Identified Bugs

- **install_packages_dialog_threadsafe()**: The return value is discarded. Either fix it to be synchronous or use a proper callback/future mechanism.
- **_find_port()** in code_drop_server.py: Add a maximum iteration count to prevent infinite loops.
- **_append_basic_tools()** in omega_init.py: This function is defined but never called -- it appears to be dead code. Either integrate it or remove it.

---

## Detailed Analysis per Module

### omega_agent/omega_agent.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 44 |
| **Complexity** | Low (thin wrapper) |
| **Risk without tests** | Low currently, high if logic is added |

The class is a straightforward subclass of litemind.agent.Agent that adds no behavior. The only value in testing is ensuring the constructor signature remains compatible with how omega_init.py calls it.

### omega_agent/napari_bridge.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 152 |
| **Complexity** | High (threading, queues, closures) |
| **Risk without tests** | Critical |

Key untested behaviors:
- qt_code_executor closure captures viewer from the constructor scope
- ExceptionGuard handling inside the closure puts the guard on the response queue AND calls enqueue_exception
- _execute_in_napari_context timeout of 300 seconds
- get_viewer_info wraps the delegated call with a try/except that returns a fallback string
- take_snapshot converts numpy array to PIL image

### omega_agent/omega_init.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 210 |
| **Complexity** | Medium-High (many conditional imports, feature checks) |
| **Risk without tests** | High |

Key untested behaviors:
- Tool context dictionary construction with all required keys
- Conditional addition of ImageDenoisingTool (platform check)
- Conditional addition of NapariViewerVisionTool (vision availability check)
- Conditional addition of builtin web search tool (model feature check)
- System message formatting with personality and didactic templates
- Dead code: _append_basic_tools() is defined but never called

### omega_agent/prompts.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 50 |
| **Complexity** | Low (static data) |
| **Risk without tests** | Medium |

The PERSONALITY dict should be tested to ensure all keys referenced by the widget exist. The SYSTEM template should be tested to ensure {personality} and {didactics} placeholders are correctly substituted.

### llm/litemind_api.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 162 |
| **Complexity** | Medium (global state, LRU cache, API initialization) |
| **Risk without tests** | High |

Key untested behaviors:
- get_litemind_api() uses a module-level global __litemind_api and calls set_api_key() for three providers on first invocation
- get_model_list() is @lru_cache decorated -- cannot be tested for cache invalidation
- is_llm_available() filters API implementations -- complex logic untested
- get_llm() falls back to api.get_best_model() when model_name is None

### llm/llm.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 86 |
| **Complexity** | Medium |
| **Risk without tests** | Medium |

Key untested behaviors:
- generate() correctly constructs messages with system prompt, user prompt, and template variables
- Temperature and model_name fallback to instance defaults when None is passed
- The method returns response directly from _api.generate_text() -- no test that the return type is list[Message]

### llm/api_keys/api_key.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 69 |
| **Complexity** | Medium (environment variables, Qt app creation, conditional dialog) |
| **Risk without tests** | Medium |

Key untested behaviors:
- set_api_key() modifies os.environ -- side effect not tested
- is_api_key_available() uses dict(os.environ) which creates a copy -- this works but is unusual
- The function creates a Qt app (get_or_create_qt_app()) as a side effect of checking an API key

### llm/api_keys/api_key_vault_dialog.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 201 |
| **Complexity** | Medium-High (Qt dialog, state machine) |
| **Risk without tests** | Medium |

Key untested behaviors:
- _already_asked_api_key module-level dict prevents re-asking but is never reset
- request_if_needed_api_key_dialog() returns None if already asked, which is indistinguishable from "user declined"
- enter_button_clicked() silently catches InvalidToken and only prints -- no user feedback in the UI
- reset_button_clicked() clears and repopulates the layout -- dynamic UI manipulation untested
- get_api_key() sets self.api_key = None after returning it -- one-shot read pattern

### chat_server/chat_server.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 537 |
| **Complexity** | High (async WebSocket, threading, FastAPI, Uvicorn) |
| **Risk without tests** | Critical |

Key untested behaviors:
- WebSocket lifecycle (connect, message exchange, disconnect, error)
- sync_handler() creates tasks on self.event_loop which is None initially
- async_run_in_executor() runs blocking agent code in executor
- start_chat_server() spawns a thread and polls with while not chat_server.running -- but running is set to True in __init__, so this loop never executes (the condition is immediately false)
- stop() uses sleep(2) for cleanup -- unreliable
- All notify_user_omega_* functions use inner closure scope -- not independently testable

### chat_server/chat_response.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 16 |
| **Complexity** | Trivial |
| **Risk without tests** | Low |

### _widget.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 592 |
| **Complexity** | Medium (Qt UI, configuration, server lifecycle) |
| **Risk without tests** | High |

Key untested behaviors:
- _preferred_models() mutates the input list in-place via list.sort(key=...) -- side effects untested
- _start_omega() catches all exceptions but only prints to console -- no user notification beyond the print
- The viewer destroyed signal connection wraps in try/except -- silently fails if napari API changes

### microplugin/microplugin_window.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 128 |
| **Complexity** | Medium-High (singleton, inheritance, dynamic sizing) |
| **Risk without tests** | High |

### microplugin/formating/black_formating.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 42 |
| **Complexity** | Low |
| **Risk without tests** | Medium (silent failures) |

### microplugin/code_editor/python_syntax_highlighting.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 249 |
| **Complexity** | Medium (regex patterns, multi-line state machine) |
| **Risk without tests** | Low-Medium |

### microplugin/code_editor/python_code_editor_widget.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 142 |
| **Complexity** | Medium |
| **Risk without tests** | Medium |

The auto-indent logic has a known weakness: any(kw in line for kw in ["if", ...]) matches substrings (e.g., "elif" contains "if", "notify" contains "not"). This would benefit from tests using word boundary checks.

### microplugin/network/code_drop_server.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 114 |
| **Complexity** | Medium-High (multicast, threading, sockets) |
| **Risk without tests** | Medium-High |

### microplugin/network/code_drop_client.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 176 |
| **Complexity** | High (threading, sockets, dynamic class creation) |
| **Risk without tests** | Medium-High |

### utils/qt/package_dialog.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 76 |
| **Complexity** | Low-Medium |
| **Risk without tests** | Medium (thread-safe variant appears broken) |

### utils/qt/qt_app.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 22 |
| **Complexity** | Low |
| **Risk without tests** | Low |

### utils/qt/one_time_disclaimer_dialog.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 49 |
| **Complexity** | Low |
| **Risk without tests** | Low-Medium |

### utils/qt/download_file_qt.py

| Aspect | Status |
|--------|--------|
| **Test exists** | No |
| **Lines of code** | 171 |
| **Complexity** | Medium (threading, network I/O, progress UI) |
| **Risk without tests** | Medium |
