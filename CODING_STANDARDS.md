# Coding Standards

## Implementation Standards

- **Separation of concerns**: Maintain clear separation in both files and directories.

- **Clean code**: Keep code as clean as possible.

- **Short functions**: Keep methods/functions as short as possible.

- **Use classes**: Organize functionality with classes to reduce code duplication if possible.

## Documentation Standards

- **Docstrings**: Always include comprehensive docstrings for classes and functions.

- **Inline comments**: Keep inline comments minimal. Only comment tricky logic.
  - ✅ Good: Explaining why something works a certain way
  - ❌ Bad: Explaining what obvious code does

- **Type hints**: Use type hints for all function parameters and return types.
  - Required: Function signatures
  - Optional: Local variables, class variables
  - Run `mypy src/` to verify type correctness (for Python projects)
