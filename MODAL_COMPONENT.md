# Modal Component Documentation

## Overview

The Modal component is a reusable Blazor component modeled after Bootstrap modals, designed to integrate seamlessly with the Car Lister application's design system.

## Features

- **Responsive Design**: Works on all screen sizes
- **Multiple Sizes**: Default, Small, Large, and Extra Large
- **Customizable**: Header, body, and footer sections
- **Accessibility**: Proper ARIA attributes and keyboard navigation
- **Animation**: Smooth fade-in/out transitions
- **Backdrop Control**: Configurable backdrop click behavior
- **Escape Key**: Close modal with Escape key (configurable)

## Usage

### Basic Modal

```razor
<Modal @ref="myModal" 
       Title="My Modal" 
       IsVisible="showModal" 
       IsVisibleChanged="OnModalChanged">
    <Body>
        <p>Your content goes here</p>
    </Body>
    <Footer>
        <button class="btn btn-secondary" @onclick="CloseModal">Cancel</button>
        <button class="btn btn-primary" @onclick="SaveData">Save</button>
    </Footer>
</Modal>
```

### Code Behind

```csharp
@code {
    private bool showModal = false;
    private Modal myModal;

    private async Task ShowModal()
    {
        showModal = true;
        await myModal?.Show();
    }

    private async Task CloseModal()
    {
        showModal = false;
        await myModal?.Hide();
    }

    private async Task OnModalChanged(bool isVisible)
    {
        showModal = isVisible;
        await Task.CompletedTask;
        StateHasChanged();
    }
}
```

## Parameters

| Parameter              | Type                  | Default   | Description                                    |
| ---------------------- | --------------------- | --------- | ---------------------------------------------- |
| `IsVisible`            | `bool`                | `false`   | Controls modal visibility                      |
| `IsVisibleChanged`     | `EventCallback<bool>` | -         | Event fired when visibility changes            |
| `Title`                | `string`              | `""`      | Modal title text                               |
| `Body`                 | `RenderFragment`      | -         | Main content area                              |
| `Footer`               | `RenderFragment`      | -         | Footer content area                            |
| `ShowHeader`           | `bool`                | `true`    | Show/hide header section                       |
| `ShowFooter`           | `bool`                | `true`    | Show/hide footer section                       |
| `ShowCloseButton`      | `bool`                | `true`    | Show/hide X button                             |
| `Fade`                 | `bool`                | `true`    | Enable fade animation                          |
| `CloseOnBackdropClick` | `bool`                | `true`    | Close when clicking backdrop                   |
| `CloseOnEscape`        | `bool`                | `true`    | Close when pressing Escape                     |
| `Size`                 | `ModalSize`           | `Default` | Modal size (Default, Small, Large, ExtraLarge) |

## Modal Sizes

- **Default**: Standard modal width (500px max)
- **Small**: Compact modal (300px max)
- **Large**: Wide modal (800px max)
- **ExtraLarge**: Extra wide modal (1140px max)

## Methods

### Show()
```csharp
await myModal.Show();
```

### Hide()
```csharp
await myModal.Hide();
```

### SetVisible(bool visible)
```csharp
await myModal.SetVisible(true);
```

## Events

### OnShow
Fired when the modal becomes visible.

### OnHide
Fired when the modal is hidden.

## Styling

The modal component uses the `modal.css` stylesheet which includes:

- Blue gradient header (matching app theme)
- Responsive design
- Smooth animations
- Custom scrollbars
- Mobile-friendly layout

## Example Page

Visit `/modal-example` to see the modal component in action with various configurations.

## Integration Notes

- The modal component is located in `Shared/Modal.razor`
- Styles are in `wwwroot/css/modal.css`
- Example usage is in `Pages/ModalExample.razor`
- Follows the existing blue color scheme and modern UI patterns
