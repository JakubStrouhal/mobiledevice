using System;
using System.ComponentModel.DataAnnotations;

namespace PhoneManagement.Models;

public class Device
{
    public int Id { get; set; }

    [Required]
    public int MakeId { get; set; }
    public DeviceMake Make { get; set; }

    [Required]
    public int ModelId { get; set; }
    public DeviceModel Model { get; set; }

    [Required]
    [StringLength(100)]
    public string SerialNumber { get; set; }

    public decimal? BuyingPrice { get; set; }

    [Required]
    public DeviceStatus Status { get; set; } = DeviceStatus.InStock;

    [StringLength(50)]
    public string? Dealer { get; set; }

    public DateTime? PurchaseDate { get; set; }

    public string? Note { get; set; }

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public ICollection<DeviceAssignment> Assignments { get; set; }
}

public enum DeviceStatus
{
    InStock,
    Issued,
    Terminated
}
